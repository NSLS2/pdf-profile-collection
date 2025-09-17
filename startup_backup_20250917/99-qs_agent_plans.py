from confluent_kafka import Producer
from nslsii.kafka_utils import _read_bluesky_kafka_config_file
import msgpack
import json

import redis

def agent_directive(tla, name, doc):
    """
    Issue any directive to a listening agent by name/uid.
    Parameters
    ----------
    tla : str
        Beamline three letter acronym
    name : str
        Unique agent name. These are generated using xkcdpass for names like:
        "agent-exotic-farm"
        "xca-clever-table"
    doc : dict
        This is the message to pass to the agent. It must take the form:
        {"action": method_name,
         "args": (arguments,),
         "kwargs: {keyword:argument}
        }
    Returns
    -------
    """
    kafka_config = _read_bluesky_kafka_config_file("/etc/bluesky/kafka.yml")
    producer_config = dict()
    producer_config.update(kafka_config["runengine_producer_config"])
    producer_config["bootstrap.servers"] = ",".join(kafka_config["bootstrap_servers"])
    agent_producer = Producer(producer_config)

    # All 3 steps should happen for each message publication
    agent_producer.produce(topic=f"{tla}.mmm.bluesky.agents", key="", value=msgpack.dumps((name, doc)))
    agent_producer.poll(0)
    agent_producer.flush()
    yield from bps.null()

# def agent_sample_count(motor, position: float, exposure: float, *, sample_number: int, md=None):
#     yield from bps.mv(motor, position)
#     _md = dict(
#         Grid_X=Grid_X.read(),
#         Grid_Y=Grid_Y.read(),
#         Grid_Z=Grid_Z.read(),
#         Det_1_X=Det_1_X.read(),
#         Det_1_Y=Det_1_Y.read(),
#         Det_1_Z=Det_1_Z.read(),
#         ring_current=ring_current.read(),
#         BStop1=BStop1.read(),
#     )
#     _md.update(get_metadata_for_sample_number(bt, sample_number))
#     _md.update(md or {})
#     yield from simple_ct([pe1c], exposure, md=_md)





def agent_redisAware_XRDcount(position: float, *, md=None):
    rkvs = redis.Redis(host="info.pdf.nsls2.bnl.gov", port=6379, db=0)  # redis key value store
    #fixing motor for now
    motor = Grid_X

    #getting XRD distance
    target_dist = float(rkvs.get('PDF:bl_config:Det_1_Z:far').decode('utf-8'))
    print ('moving to XRD position')
    yield from bps.mv(Det_1_Z, target_dist)
    #put xrd-speicifc config in place
    #my_config = {'auto_mask': False,
    #'user_mask': '/nsls2/data2/pdf/legacy/processed/xpdacq_data/user_data/my_mask_xrd.npy',
    #'method': 'splitpixel'}
    #p_my_config = json.dumps(my_config)
    #rkvs.set('PDF:xpdacq:user_config',p_my_config)

    #getting the user_config from redis
    p_my_config = rkvs.get("PDF:xpdacq:user_config:far")
    user_config = json.loads(p_my_config) #here is the user_config

    if bool(rkvs.exists('PDF:xpdacq:xrd_sample_number')):
        sample_number = int(rkvs.get('PDF:xpdacq:xrd_sample_number').decode('utf-8')) #here is the sample num
    else:
        print ('missing sample number in redis')    

    #gettting sample metadata from redis
    if bool(rkvs.exists('PDF:xpdacq:sample_dict')):
        p_info = rkvs.get('PDF:xpdacq:sample_dict')
    else:
        print ('missing bt sample info, need to stow_bt_sample_info')
    all_sample_info = json.loads(p_info)
    sample_name = list(all_sample_info)[sample_number]
    this_sample_md = all_sample_info[sample_name] #here is the sample metadata from bt

    #get the XRD calibration info from redis
    xrd_calib_md = json.loads(rkvs.get('PDF:xpdacq:xrd_calibration_md'))

    #getting exposure time from redis
    exposure = float(rkvs.get('PDF:desired_exposure_time').decode('utf-8'))
    #print ('exposure is '+str(exposure))

    yield from bps.mv(motor, position)
    _md = dict(
        Grid_X=Grid_X.read(),
        Grid_Y=Grid_Y.read(),
        Grid_Z=Grid_Z.read(),
        Det_1_X=Det_1_X.read(),
        Det_1_Y=Det_1_Y.read(),
        Det_1_Z=Det_1_Z.read(),
        ring_current=ring_current.read(),
        BStop1=BStop1.read(),
        user_config=user_config,
        calibration_md = xrd_calib_md,
    )
    #_md.update(get_metadata_for_sample_number(bt, sample_number))
    _md.update(this_sample_md)
    _md.update(md or {})
    yield from simple_ct([pe1c], exposure, md=_md)


##############

def agent_move_and_measure_hanukkah23(x, y,
        xpdacq_sample_num = None,
        exposure = None,
        md=None):
    
    xlims = (-165, -88)
    ylims = (9, 87)

    if not (xlims[0] < x < xlims[1]):
        raise ValueError(f'The target {x=} is out of bounds {xlims}')
        
    if not (ylims[0] < y < ylims[1]):
        raise ValueError(f'The target {y=} is out of bounds {ylims}')

    xstage = OT_stage_2_X
    ystage = OT_stage_2_Y

    rkvs = redis.Redis(host="info.pdf.nsls2.bnl.gov", port=6379, db=0)  # redis key value store
    
    if xpdacq_sample_num is None:
        xpdacq_sample_num = int(rkvs.get('PDF:xpdacq:sample_number').decode('utf-8')) #here is the sample num

    #now getting sample info from redis, such as exposure and sample_number
    if exposure == None:
        if bool(rkvs.exists('PDF:desired_exposure_time')):
            exposure = float(rkvs.get('PDF:desired_exposure_time'))
        else:
            print ("missing exposure time in redis, defaulting to 10 s")
            exposure = 10.0

    #assured that our requested position is in bounds, we can move.
    yield from bps.mv(xstage, x, ystage, y)

    if bool(rkvs.exists('PDF:xpdacq:sample_dict')):
        p_info = rkvs.get('PDF:xpdacq:sample_dict')
    else:
        print ('missing bt sample info, need to stow_bt_sample_info')
    
    all_sample_info = json.loads(p_info)
    sample_name = list(all_sample_info)[xpdacq_sample_num]
    this_sample_md = all_sample_info[sample_name] #here is the sample metadata from bt 
    calib_md = json.loads(rkvs.get('PDF:xpdacq:pdf_calibration_md'))
    
    #getting the user_config from redis
    p_my_config = rkvs.get("PDF:xpdacq:user_config:near")
    user_config = json.loads(p_my_config) #here is the user_config


    cx = -128.85
    cy = 49.91
    cxy = (cx,cy)
    rx = xstage.read()['OT_stage_2_X']['value']-cxy[0],
    ry = ystage.read()['OT_stage_2_Y']['value']-cxy[1],
    
    _md = {'more_info': dict(
        xstage=xstage.read(),
        ystage=ystage.read(),
        center_xy = cxy,
        
        rel_to_center_x = rx,
        rel_to_center_y = ry,
        rel_to_center_xy = (rx,ry),
    
        Grid_X=Grid_X.read(),
        Grid_Y=Grid_Y.read(),
        Grid_Z=Grid_Z.read(),
        Det_1_X=Det_1_X.read(),
        Det_1_Y=Det_1_Y.read(),
        Det_1_Z=Det_1_Z.read(),
        ring_current=ring_current.read(),
        BStop1=BStop1.read()),

        'user_config':user_config,
        
        'calibration_md': calib_md,
    }
    #_md.update(get_metadata_for_sample_number(bt, sample_number))
    _md.update(this_sample_md)
    _md.update(md or {})
    print (f"{exposure=}")
    yield from jog([pilatus1], exposure, ystage, y,y, md=_md)
    #yield from simple_ct([pilatus1], exposure, md=_md)


##############
def agent_take_the_shot(xpdacq_sample_num=0, exposure=5, md=None):
    rkvs = redis.Redis(host="info.pdf.nsls2.bnl.gov", port=6379, db=0)  # redis key value store

    if bool(rkvs.exists('PDF:xpdacq:sample_dict')):
        p_info = rkvs.get('PDF:xpdacq:sample_dict')
    else:
        print ('missing bt sample info, need to stow_bt_sample_info')
    
    all_sample_info = json.loads(p_info)
    sample_name = list(all_sample_info)[xpdacq_sample_num]
    this_sample_md = all_sample_info[sample_name] #here is the sample metadata from bt 
    calib_md = json.loads(rkvs.get('PDF:xpdacq:xrd_calibration_md'))
    
    #getting the user_config from redis
    p_my_config = rkvs.get("PDF:xpdacq:user_config:far")
    user_config = json.loads(p_my_config) #here is the user_config

    _md = dict(
        Grid_X=Grid_X.read(),
        Grid_Y=Grid_Y.read(),
        Grid_Z=Grid_Z.read(),
        Det_1_X=Det_1_X.read(),
        Det_1_Y=Det_1_Y.read(),
        Det_1_Z=Det_1_Z.read(),
        ring_current=ring_current.read(),
        BStop1=BStop1.read(),
        user_config=user_config,
        calibration_md = calib_md,
    )
    #_md.update(get_metadata_for_sample_number(bt, sample_number))
    _md.update(this_sample_md)
    _md.update(md or {})
    yield from simple_ct([pe1c], exposure, md=_md)

##%%%%%%%%%%%##

def agent_redisAware_XRDcount_dos(md=None):
    rkvs = redis.Redis(host="info.pdf.nsls2.bnl.gov", port=6379, db=0)  # redis key value store

    #getting the user_config from redis
    p_my_config = rkvs.get("PDF:xpdacq:user_config:far")
    user_config = json.loads(p_my_config) #here is the user_config
    
    #getting the current sample number from redis
    sample_number = 0
    
    #gettting sample metadata from redis
    p_info = rkvs.get('PDF:xpdacq:sample_dict')
    all_sample_info = json.loads(p_info)
    sample_name = list(all_sample_info)[sample_number]
    this_sample_md = all_sample_info[sample_name] #here is the sample metadata from bt
    
    #get the PDF calibration info from redis
    pdf_calib_md = json.loads(rkvs.get('PDF:xpdacq:xrd_calibration_md'))

    #getting exposure time from redis
    exposure = 5.0
    print ('exposure is '+str(exposure))

    _md = dict(
        Grid_X=Grid_X.read(),
        Grid_Y=Grid_Y.read(),
        Grid_Z=Grid_Z.read(),
        Det_1_X=Det_1_X.read(),
        Det_1_Y=Det_1_Y.read(),
        Det_1_Z=Det_1_Z.read(),
        ring_current=ring_current.read(),
        BStop1=BStop1.read(),
        user_config=user_config,
        calibration_md=pdf_calib_md,
    )
    _md.update(this_sample_md)
    _md.update(md or {})
    yield from simple_ct([pe1c], exposure, md=_md)


    
##%%%%%%%%####
def agent_redisAware_PDFcount(position: float, *, md=None):
    rkvs = redis.Redis(host="info.pdf.nsls2.bnl.gov", port=6379, db=0)  # redis key value store
    #fixing motor for now
    motor = Grid_X

    #getting PDF distance
    target_dist = float(rkvs.get('PDF:bl_config:Det_1_Z:near').decode('utf-8'))
    print ('moving to PDF position')
    yield from bps.mv(Det_1_Z, target_dist)
    #put pdf-specific config in place
    #my_config = {'auto_mask': False,
    #'user_mask': '/nsls2/data2/pdf/legacy/processed/xpdacq_data/user_data/my_mask_pdf.npy',
    #'method': 'splitpixel'}
    #p_my_config = json.dumps(my_config)
    #rkvs.set('PDF:xpdacq:user_config',p_my_config)

    #getting the user_config from redis
    p_my_config = rkvs.get("PDF:xpdacq:user_config:near")
    user_config = json.loads(p_my_config) #here is the user_config
    
    #getting the current sample number from redis
    #check if this exists, then read
    if bool(rkvs.exists('PDF:xpdacq:pdf_sample_number')):
        sample_number = int(rkvs.get('PDF:xpdacq:pdf_sample_number').decode('utf-8')) #here is the sample num
    else:
        print ('missing sample number in redis')
    
    #gettting sample metadata from redis
    p_info = rkvs.get('PDF:xpdacq:sample_dict')
    all_sample_info = json.loads(p_info)
    sample_name = list(all_sample_info)[sample_number]
    this_sample_md = all_sample_info[sample_name] #here is the sample metadata from bt
    
    #get the PDF calibration info from redis
    #print ('loading calibration from redis.\n\n\n')
    pdf_calib_md = json.loads(rkvs.get('PDF:xpdacq:pdf_calibration_md'))
    #print ('got the following md '+str(pdf_calib_md))

    #getting exposure time from redis
    exposure = float(rkvs.get('PDF:desired_exposure_time').decode('utf-8'))
    print ('exposure is '+str(exposure))

    yield from bps.mv(motor, position)
    _md = dict(
        Grid_X=Grid_X.read(),
        Grid_Y=Grid_Y.read(),
        Grid_Z=Grid_Z.read(),
        Det_1_X=Det_1_X.read(),
        Det_1_Y=Det_1_Y.read(),
        Det_1_Z=Det_1_Z.read(),
        ring_current=ring_current.read(),
        BStop1=BStop1.read(),
        user_config=user_config,
        #this_sample_md = this_sample_md,
        calibration_md=pdf_calib_md,
        #calibration_md=None,
        #calibration_md2=pdf_calib_md,
    )
    #print ('\n\nmd is '+str(md))
    #print ('_md is '+str(_md))
    #_md.update(get_metadata_for_sample_number(bt, sample_number))
    _md.update(this_sample_md)
    _md.update(md or {})
    #print ('\n\nbut now md is '+str(md))
    #print ('and _md is '+str(_md))
    yield from simple_ct([pe1c], exposure, md=_md)

###############


def agent_redisAware_count(position: float, *, md=None):
    #fixing motor for now
    motor = Grid_X


    #getting the user_config from redis
    rkvs = redis.Redis(host="info.pdf.nsls2.bnl.gov", port=6379, db=0)  # redis key value store
    p_my_config = rkvs.get("PDF:xpdacq:user_config")
    user_config = json.loads(p_my_config) #here is the user_config

    #getting the current sample number from redis
    sample_number = int(rkvs.get('PDF:xpdacq:sample_number').decode('utf-8')) #here is the sample num
    
    #gettting sample metadata from redis
    p_info = rkvs.get('PDF:xpdacq:sample_dict')
    all_sample_info = json.loads(p_info)
    sample_name = list(all_sample_info)[sample_number]
    this_sample_md = all_sample_info[sample_name] #here is the sample metadata from bt

    #getting exposure time from redis
    exposure = float(rkvs.get('PDF:desired_exposure_time').decode('utf-8'))
    print ('exposure is '+str(exposure))

    yield from bps.mv(motor, position)
    _md = dict(
        Grid_X=Grid_X.read(),
        Grid_Y=Grid_Y.read(),
        Grid_Z=Grid_Z.read(),
        Det_1_X=Det_1_X.read(),
        Det_1_Y=Det_1_Y.read(),
        Det_1_Z=Det_1_Z.read(),
        ring_current=ring_current.read(),
        BStop1=BStop1.read(),
        user_config=user_config,
    )
    #_md.update(get_metadata_for_sample_number(bt, sample_number))
    _md.update(this_sample_md)
    _md.update(md or {})
    yield from simple_ct([pe1c], exposure, md=_md)
               


def agent_sample_count(motor, position: float, exposure: float, *, sample_number: int, md=None):
    rkvs = redis.Redis(host="info.pdf.nsls2.bnl.gov", port=6379, db=0)  # redis key value store
    p_my_config = rkvs.get("PDF:xpdacq:user_config")
    user_config = json.loads(p_my_config)
    yield from bps.mv(motor, position)
    _md = dict(
        Grid_X=Grid_X.read(),
        Grid_Y=Grid_Y.read(),
        Grid_Z=Grid_Z.read(),
        Det_1_X=Det_1_X.read(),
        Det_1_Y=Det_1_Y.read(),
        Det_1_Z=Det_1_Z.read(),
        ring_current=ring_current.read(),
        BStop1=BStop1.read(),
        user_config=user_config,
    )
    _md.update(get_metadata_for_sample_number(bt, sample_number))
    _md.update(md or {})
    yield from simple_ct([pe1c], exposure, md=_md)
               
@bpp.run_decorator(md={})
def agent_driven_nap(delay: float, *, delay_kwarg: float = 0):
    """Ensuring we can auto add 'agent_' plans and use args/kwargs"""
    if delay_kwarg:
        yield from bps.sleep(delay_kwarg)
    else:
        yield from bps.sleep(delay)

               
def agent_print_glbl_val(key: str):
    """
    Get common global values from a namespace dictionary.
    Keys
    ---
    frame_acq_time : Frame rate acquisition time
    dk_window : dark window time
    """
    print(glbl[key])
    yield from bps.null()


def agent_set_glbl_val(key: str, val: float):
    """
    Set common global values from a namespace dictionary.
    Keys
    ---
    frame_acq_time : Frame rate acquisition time
    dk_window : dark window time
    """
    glbl[key] = val
    yield from bps.null()
