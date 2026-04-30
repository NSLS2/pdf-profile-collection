# main plans

file_loading_timer.start()

# this was the original toy plan
def acquisition_plan(dets, motors, fs, sample_name, images_per_set=None):
    '''
        This is testing a simple acquisition plan.
        Here we open shutter, take an image, close shutter, take a dark then
            stop.
        dets : dets to read from
        motors: motors to take readings from
            (for later use)
        fs : the fast shutter
        sample_name : the sample name
    '''
    start_time = time.time()
    def myplan():
        
        for det in dets:
            if images_per_set is not None:
                yield from bps.mov(det.images_per_set, images_per_set)

        for det in dets:
            yield from bps.stage(det)

        yield from bps.sleep(1)
        # close fast shutter, now take a dark
        # yield from bps.mov(fs,0)
        yield from bps.mov(fb2.flt4, 0)
        yield from trigger_and_read(dets + motors, name='dark')
        # open fast shutter
        # yield from bps.mov(fs,1)
        yield from bps.mov(fb2.flt4, 1)
        # for the motors, trigger() won't be called since it doesn't exist
        yield from trigger_and_read(dets + motors, name='primary')
        for det in dets:
            yield from bps.unstage(det)

        
    yield from bpp.run_wrapper(myplan(), md=dict(sample_name=sample_name))
    end_time = time.time()
    print(f'Duration: {end_time - start_time:.3f} sec')

file_loading_timer.stop()
