"""Used for tutorial `Using Devices`."""

# Import bluesky and ophyd
import asyncio
from dataclasses import dataclass
from functools import cached_property
from math import isclose
from typing import Annotated as A
from typing import ClassVar
from bisect import bisect
from time import perf_counter,sleep

from IPython import get_ipython
from ophyd_async.core import (
    MovableLogic,
    SignalR,
    SignalRW,
    StandardMovable,
    StandardReadable,
    StrictEnum,
    Reference,
    TimeoutCalculator,
    derived_signal_r,
    init_devices,
)
from ophyd_async.core import StandardReadableFormat as Format
from ophyd_async.epics.core import EpicsDevice, PvSuffix

class Lakeshore336Switch(StrictEnum):
    OFF = "OFF"
    ON = "ON"

class Lakeshore336LoopMode(StrictEnum):
    OFF = "OFF"
    PID = "PID"
    ZONE = "ZONE"
    OLOOP = "OPEN LOOP"
    MON = "MONITOR"
    WARM = "WARMUP"

class Lakeshore336RangeSelect(StrictEnum):
    OFF = "OFF"
    RANGE1 = "RANGE 1"
    RANGE2 = "RANGE 2"
    RANGE3 = "RANGE 3"

class Lakeshore336Resistance(StrictEnum):
    LO25 = "25 OHM"
    HI50 = "50 OHM"
    
class Lakeshore336LoopInput(StrictEnum):
    NONE = "NONE"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"
    D5 = "D5"

class LakeShore336Input(EpicsDevice, StandardReadable):
    """One Lake Shore 336 temperature input."""

    temp: A[SignalR[float], PvSuffix("T-I"), Format.HINTED_SIGNAL]
    tempc: A[SignalR[float], PvSuffix("T:C-I")]
    raw: A[SignalR[float], PvSuffix("Val:Sens-I")]
    status: A[SignalR[str], PvSuffix("T-Sts")]

    def __init__(
        self,
        prefix: str,
        channel: Lakeshore336LoopInput,
        *,
        name: str = "",
    ) -> None:
        """`channel` is this input's own identity (A, B, C, ...), independent of
        whichever loop (if any) is currently reading it as a control input."""
        self.channel = channel
        super().__init__(prefix, name=name)


@dataclass
class LakeShore336LoopLogic(MovableLogic[float]):
    """Define what a move means for one Lake Shore control loop."""

    tolerance: float
    settle_time: float
    move_timeout: float
    p: SignalRW[float]
    i: SignalRW[float]
    d: SignalRW[float]
    ramp: SignalRW[float]

    delta = None

    async def check_move(self, new_position):
        if new_position < 5:
            raise ValueError
        elif new_position > 550:
            raise ValueError

    async def delta_t(
        self,
        old_position: float,
        new_position: float,
    ) -> None:
        self.delta = new_position - old_position

    async def set_pids(
        self,
        new_position: float
    ) -> None:

        if self.delta > .5:
            temp_thresholds = [140,270,300]
            pids = [(50,10,1),(25,6,3),(26,5,3),(26,5,3)]

        elif self.delta < -.5:
            temp_thresholds = [140,200]
            pids = [(25,4,3),(25,6,3),(35,8,3)]

        else:
            return

        pid_selector = bisect(temp_thresholds,new_position)
        _p,_i,_d = pids[pid_selector]

        await self.p.set(_p)
        await self.i.set(_i)
        await self.d.set(_d)        

    async def calculate_timeout(
        self,
        old_position: float,
        new_position: float,
    ) -> float:

        await self.delta_t(old_position,new_position)
        print(f"Delta = {self.delta:.2f}")

        await self.set_pids(new_position)

        ramp_rate = await self.ramp.get_value()  # perhaps degrees/minute

        if ramp_rate == 0:
            ramp_rate = .015 # K/s

        travel_time = abs(self.delta) / ramp_rate * 60
        timeout = travel_time + self.settle_time + 30

        print(f"{timeout:.2f} Seconds to complete the temp change")

        return timeout

    async def move(
        self, new_position: float, timeout: TimeoutCalculator
        ) -> None:
        """Write the setpoint and wait for readback to settle around it."""

        start_time = perf_counter()

        original_temp = await self.readback.get_value()

        print(f"Changing temp from {original_temp:.2f} to {new_position:.2f}")

        loop = asyncio.get_running_loop()
        settled = asyncio.Event()
        settle_timer: asyncio.TimerHandle | None = None
        
        def update_settled_state(reading) -> None:
            nonlocal settle_timer
            value = reading[self.readback.name]["value"]
            in_tolerance = isclose(
                value, new_position, rel_tol=0.0, abs_tol=self.tolerance
            )

            if in_tolerance and settle_timer is None:
                # Start a timer the first time the readback enters tolerance.
                # It is cancelled below if a later update leaves tolerance.
                settle_timer = loop.call_later(self.settle_time, settled.set)
            elif not in_tolerance and settle_timer is not None:
                settle_timer.cancel()
                settle_timer = None
                settled.clear()

        # Subscribe before writing so that a fast readback update cannot be missed.
        self.readback.subscribe_reading(update_settled_state)
        try:
            # await self.setpoint.set(new_position, timeout=timeout())
            await self.setpoint.set(new_position)
            async with asyncio.timeout(timeout()):
                await settled.wait()
                end_time = perf_counter()
                print(f"Temp change completed in {(end_time - start_time)/60:.2f} mins")
        finally:
            if settle_timer is not None:
                settle_timer.cancel()
            self.readback.clear_sub(update_settled_state)

class LakeShore336Loop(EpicsDevice, StandardReadable, StandardMovable[float]):
    """
    One heater/control loop.

    setpoint, PID, heater range, ramp settings, etc.
    """

    enbl: A[
        SignalRW[str], PvSuffix("Enbl-Sel")
    ]  # this is the general on and off for the loop

    sp: A[
        SignalRW[float],
        PvSuffix("T-SP"),
        Format.CONFIG_SIGNAL
    ]

    sprdk: A[
        SignalR[float],
        PvSuffix("T-RB"),
        Format.HINTED_SIGNAL
    ]

    p: A[
        SignalRW[float],
        PvSuffix(write_suffix="Gain:P-SP", read_suffix="Gain:P-RB"),
        Format.CONFIG_SIGNAL,
    ]
    i: A[
        SignalRW[float],
        PvSuffix(write_suffix="Gain:I-SP", read_suffix="Gain:I-RB"),
        Format.CONFIG_SIGNAL,
    ]
    d: A[
        SignalRW[float],
        PvSuffix(write_suffix="Gain:D-SP", read_suffix="Gain:D-RB"),
        Format.CONFIG_SIGNAL,
    ]
    ramp: A[
        SignalRW[float],
        PvSuffix(write_suffix="Val:Ramp-SP", read_suffix="Val:Ramp-RB"),
        Format.CONFIG_SIGNAL,
    ]

    range: A[
        SignalRW[str],
        PvSuffix(write_suffix="Val:Range-Sel", read_suffix="Val:Range-Sts"),
        Format.CONFIG_SIGNAL,
    ]

    maxi: A[
        SignalRW[float],
        PvSuffix("Out:MaxI-SP")]

    loop_mode: A[
        SignalRW[str],
        PvSuffix("Mode-Sel"),
        Format.CONFIG_SIGNAL
        ]

    resistance: A[
        SignalRW[str],
        PvSuffix("Out:R-SP"),
        Format.CONFIG_SIGNAL
        ]

    ramp_enbl: A[
        SignalRW[str],
        PvSuffix("Enbl:Ramp-Sel"),
        Format.CONFIG_SIGNAL
        ]

    autotune: A[
        SignalRW[str],
        PvSuffix(write_suffix="Mode:ATune-Sel", read_suffix="Mode:ATune-Sts"),
    ]

    loop_in_sel: A[
        SignalRW[Lakeshore336LoopInput],
        PvSuffix("Out-Sel"),
        Format.CONFIG_SIGNAL
        ]

    loop_in_rb: A[
        SignalRW[Lakeshore336LoopInput],
        PvSuffix("Out-Sts"),
        Format.CONFIG_SIGNAL
        ]

    def __init__(
        self,
        prefix: str,
        loop_input: LakeShore336Input,
        *,
        tolerance: float = 0.1,
        settle_time: float = 5.0,
        move_timeout: float = 600.0,
        name: str = "",
    ) -> None:

        # Wrapped in Reference so `loop_input` (already a child of the parent
        # LakeShore336) is not re-parented under this loop too.
        self._loop_input_ref = Reference(loop_input)
        self._tolerance = tolerance
        self._settle_time = settle_time
        self._move_timeout = move_timeout
        super().__init__(prefix, name=name)

    @property
    def loop_input(self) -> LakeShore336Input:
        return self._loop_input_ref()

    async def select_input(self) -> None:
        """Point the physical loop's PID input at the channel `loop_input`
        was constructed with, so the hardware selection matches the Python
        object graph."""
        await self.loop_in_sel.set(self.loop_input.channel)

    async def get_loop_temp_k(self) -> float:
        return await self.loop_input.temp.get_value()

    @cached_property
    def movable_logic(self) -> MovableLogic[float]:
        """Connect StandardMovable to this loop's setpoint and a private
        mirror of the assigned input's temperature.

        A derived signal is used (rather than `self.loop_input.temp`
        directly) because `StandardMovable.set_name()` renames its
        `readback` signal to match this loop's name. `loop_input.temp` is
        also an independently readable child of the top-level LakeShore336
        device, so reusing it here would rename it out from under anyone
        reading that channel directly.
        """

        def temp(temp: float) -> float:
            return temp

        return LakeShore336LoopLogic(
            setpoint=self.sp,
            readback=derived_signal_r(temp, temp=self.loop_input.temp),
            tolerance=self._tolerance,
            settle_time=self._settle_time,
            move_timeout=self._move_timeout,
            p=self.p,
            i=self.i,
            d=self.d,
            ramp = self.ramp
        )
    # Max: A[SignalRW[float], PvSuffix("Out:Max-SP"), Format.CONFIG_SIGNAL]
    # Disp: A[SignalRW[float], PvSuffix("Out:Disp-SP"), Format.CONFIG_SIGNAL]

    # def __init__(self, prefix, with_pvi = False, name = ""):
    #     super().__init__(prefix, with_pvi, name)
    #     config:str


class LakeShore336(StandardReadable):
    """Master Lake Shore 336 object."""

    def __init__(
        self,
        prefix: str,
        *,
        name: str = "",
    ):

        with self.add_children_as_readables():
            self.input_a = LakeShore336Input(f"{prefix}-Chan:A}}", Lakeshore336LoopInput.A)
            self.input_b = LakeShore336Input(f"{prefix}-Chan:B}}", Lakeshore336LoopInput.B)
            self.input_c = LakeShore336Input(f"{prefix}-Chan:C}}", Lakeshore336LoopInput.C)
            self.input_d = LakeShore336Input(f"{prefix}-Chan:D}}", Lakeshore336LoopInput.D)
            self.input_d2 = LakeShore336Input(f"{prefix}-Chan:D2}}", Lakeshore336LoopInput.D2)
            self.input_d3 = LakeShore336Input(f"{prefix}-Chan:D3}}", Lakeshore336LoopInput.D3)
            self.input_d4 = LakeShore336Input(f"{prefix}-Chan:D4}}", Lakeshore336LoopInput.D4)
            self.input_d5 = LakeShore336Input(f"{prefix}-Chan:D5}}", Lakeshore336LoopInput.D5)

            self.out1 = LakeShore336Loop(f"{prefix}-Out:1}}", self.input_c, tolerance=1, settle_time=120)
            self.out2 = LakeShore336Loop(f"{prefix}-Out:2}}", self.input_a)
            self.out3 = LakeShore336Loop(f"{prefix}-Out:3}}", self.input_a)
            self.out4 = LakeShore336Loop(f"{prefix}-Out:4}}", self.input_a)

        super().__init__(name=name)

with init_devices():
    lake = LakeShore336("XF:28ID1-ES{LS336:1", name="Lakeshore")


# """
# Heres and example plan for moving the cryostat and ignoring a setpoint
# not being reached and timing out.
# """


import warnings
import asyncio

from bluesky.utils import FailedStatus

cryostat = lake.out1    

async def default_loop(loop: LakeShore336Loop):

    # Set the loop sp to the current temp so nothing moves irradically.
    curr_temp = await loop.get_loop_temp_k()
    await loop.sp.set(curr_temp)

    coros = [
        # Set input as defined in object definition
        loop.select_input(),

        loop.ramp_enbl.set(Lakeshore336Switch.ON),
        loop.ramp.set(6),
        loop.enbl.set(Lakeshore336Switch.ON),
        loop.loop_mode.set(Lakeshore336LoopMode.PID),
        loop.maxi.set(2),
        loop.resistance.set(Lakeshore336Resistance.LO25),
    ]

    await asyncio.gather(*coros)

    # Turn on the heater
    await loop.range.set(Lakeshore336RangeSelect.RANGE3)

def move_and_continue(device, target):
    """Move `device` to `target`; if it fails to settle in time, warn and
    let the plan proceed to the next point instead of aborting.

    Bluesky's RunEngine never lets the original device-side exception (e.g.
    the `TimeoutError` from a move that didn't settle) reach the plan: any
    failed status is re-raised into the plan as `bluesky.utils.FailedStatus`,
    with the real cause attached as `.__cause__`. Only a `TimeoutError` cause
    is swallowed here; anything else (an out-of-range setpoint, a dropped
    connection, ...) re-raises so it isn't silently lost in a long sweep.
    """
    try:
        yield from bps.mv(device, target)
    except FailedStatus as e:
        if not isinstance(e.__cause__, TimeoutError):
            raise
        warnings.warn(
            f"{device.name} did not settle at {target} ({e.__cause__!r}); continuing",
            RuntimeWarning,
        )
        return e
    return None


def t_list(tlist):

    failures = []
    for temp in tlist:
        exc = yield from move_and_continue(lake.out1, temp)
        if exc is not None:
            failures.append((temp, exc))

    if failures:
        print(f"{len(failures)}/{len(tlist)} setpoints did not settle:")
        for temp, exc in failures:
            print(f"  {temp}: {exc.__cause__!r}")
# Compare out to sp
# RE(bp.scan([lake.input_a.temp],lake.out1,5,400,100))