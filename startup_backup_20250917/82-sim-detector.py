import os
import time

import pandas as pd
import numpy as np

from ophyd.sim import SynSignal


class OmniaDetector(SynSignal):
    def __init__(
        self,
        dbr,
        name,
        motor1,
        motor_field1,
        motor2,
        motor_field2,
        *,
        omnia_xy_index_fp="omnia_xy_index.txt",
        **kwargs,
    ):
        self.dbr = dbr
        self.name = name
        self.motor1 = motor1
        self.motor_field1 = motor_field1
        self.motor2 = motor2
        self.motor_field2 = motor_field2

        if not os.path.exists(omnia_xy_index_fp):
            self.build_image_index()
        print(f"loading {omnia_xy_index_fp}")
        self.omnia_xy_index = pd.read_csv(
            omnia_xy_index_fp, sep="\t", header=0, index_col=0
        )

        grid_x_min = self.omnia_xy_index.Grid_X.min()
        grid_x_max = self.omnia_xy_index.Grid_X.max()
        grid_y_min = self.omnia_xy_index.Grid_Y.min()
        grid_y_max = self.omnia_xy_index.Grid_Y.max()

        # don't want to do this
        motor1.set(grid_x_min)
        motor2.set(grid_y_min)

        def _compute():
            """
            Grid_X: 8.903
            Grid_Y: 768.94725
            sample_name: omnia
            """
            print(f"_computing!")
            x = self.motor1.read()[self.motor_field1]["value"]
            y = self.motor2.read()[self.motor_field2]["value"]

            if not grid_x_min <= x <= grid_x_max:
                raise ValueError(f"motor 1 is out of bounds: {self.motor1.read()}")
            elif not grid_y_min <= y <= grid_y_max:
                raise ValueError(f"motor 2 is out of bounds: {self.motor2.read()}")
            else:
                d = np.linalg.norm(self.omnia_xy_index[["Grid_X", "Grid_Y"]] - [x, y])
                nearest_i = np.argmin(d)
                nearest_uid = self.omnia_xy_index.uid[nearest_i]
                print(f"nearest_uid: {nearest_uid}")

                image = dbr[nearest_uid].data("pe1c_image")

            return image

        super().__init__(name=name, func=_compute, **kwargs)

    def build_image_index(self):
        print(f"creating {omnia_xy_index_fp}")
        t0 = time.time()
        grid_x = []
        grid_y = []
        uids = []
        for h in self.dbr(sample_name="omnia"):
            grid_x.append(h.start["Grid_X"])
            grid_y.append(h.start["Grid_Y"])
            uids.append(h.start["uid"])

        df = pd.DataFrame(
            zip(grid_x, grid_y, uids), columns=("Grid_X", "Grid_Y", "uid")
        )
        df.to_csv(omnia_xy_index_fp, sep="\t")
        print(f"finished {omnia_xy_index_fp} in {time.time()-t0:.3}s")


def init_omnia_sim_detector():
    from databroker import Broker
    from ophyd.sim import hw

    dbr = Broker.named("pdf")
    sim = hw()

    return OmniaDetector(
        dbr=dbr,
        name="omnia_det",
        motor1=sim.motor1,
        motor_field1="motor1",
        motor2=sim.motor2,
        motor_field2="motor2",
    )
