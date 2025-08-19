import datetime
import pprint
import uuid
# from bluesky_kafka import RemoteDispatcher
from bluesky_kafka.consume import BasicConsumer
import matplotlib.pyplot as plt
import numpy as np
from tiled.client import from_profile, from_uri


import importlib
img_getpdf = importlib.import_module("img_getpdf")
img_plotter = importlib.import_module("img_plotter")
kafka_log = importlib.import_module("kafka_uti").kafka_log
bin_ndarray = importlib.import_module("kafka_uti").bin_ndarray

"--------------------------USER INPUTS------------------------------"
tiled_client = from_profile('pdf')
sandbox_tiled = from_uri("https://tiled.nsls2.bnl.gov/api/v1/metadata/xpd/sandbox")
ini_config = '/home/xf28id1/.ipython/profile_collection/scripts/pdf_Kafka/pilatus_kafka_config.ini'
k_log = kafka_log()

"--------------DO NOT TOUCH BELOW!! Unless CHLin said OK!-----------"

try:
    from nslsii import _read_bluesky_kafka_config_file  # nslsii <0.7.0
except (ImportError, AttributeError):
    from nslsii.kafka_utils import _read_bluesky_kafka_config_file  # nslsii >=0.7.0

# these two lines allow a stale plot to remain interactive and prevent
# the current plot from stealing focus.  thanks to Tom:
# https://nsls2.slack.com/archives/C02D9V72QH1/p1674589090772499
plt.ion()
plt.rcParams["figure.raise_window"] = False


def print_kafka_messages(beamline_acronym_01, beamline_acronym_02,  
                         tiled_client=tiled_client, 
                         ini_config=ini_config, 
                         sandbox_tiled=sandbox_tiled, 
                         k_log=k_log, 
                         ):
    
    print(f"Listening to Kafka messages for {beamline_acronym_01}")
    print(f"Listening to Kafka messages for {beamline_acronym_02}")

    
    def print_message(consumer, doctype, doc):
        name, message = doc
        # print(
        #     f"\n{datetime.datetime.now().isoformat()} document: {name}\n"
        # #     f"\ndocument keys: {list(message.keys())}\n"
        # #     f"\ncontents: {pprint.pformat(message)}\n"
        # )

        if (name == 'start') and ('topic' not in message):
            print(
                "\n*********************************************************\n"
                f"\n\n{datetime.datetime.now().isoformat()} documents {name}\n"
                # f"document keys: {list(message.keys())}"
                f"\n{message['uid'] = }\n")
            try:
                print(f"\n{message['topic'] = }\n")
            except KeyError:
                print(f"\nThis document has no topic.\n")
                  
            global img_analyzer
            uid = message['uid']
            meta = tiled_client[uid].start
            print(f"{meta['calibration_md']['Distance'] = }")
            
            img_analyzer = img_getpdf.img_getpdf(uid, tiled_client, sandbox_tiled, ini_config)
            
            print(f'{img_analyzer.is_pdf_xrd() = }')
        
        
        elif (name == 'stop') and ('topic' not in message):
            print(
                "\n*********************************************************\n"
                f"\n{datetime.datetime.now().isoformat()} documents {name}\n"
                f"\ndocument keys: {list(message.keys())}\n"
                f"\ncontents: {pprint.pformat(message['num_events'])}\n"
                )
            try:
                print(f"\n{message['topic'] = }\n")
            except KeyError:
                print(f"\nThis document has no topic.\n")

            stream_name = list(message['num_events'].keys())
            img_analyzer.stream_name = stream_name
            print(f'\n{stream_name = }\n')
        
        
        
        elif (name == 'event') and ('topic' in message):
            print(
                "\n*********************************************************\n"
                f"\n{datetime.datetime.now().isoformat()} documents {name}\n"
                f"\ndocument keys: {list(message.keys())}\n"
                )
            try:
                print(f"\n{message['topic'] = }\n")
            except KeyError:
                print(f"\nThis document has no topic.\n")

            dksub_uid = message["data"]['tiled_dk_sub_image']['uid']
            img_analyzer.dksub_uid = dksub_uid



        # elif (name == 'stop') and ('topic' in message) and (message['num_events']['primary']==3):
        elif (name == 'stop') and ('topic' in message):
            print(
                "\n*********************************************************\n"
                f"\n{datetime.datetime.now().isoformat()} documents {name}\n"
                f"\ndocument keys: {list(message.keys())}\n"
                f"\ncontents: {pprint.pformat(message['num_events'])}\n"
                )
            try:
                print(f"\n{message['topic'] = }\n")
            except KeyError:
                print(f"\nThis document has no topic.\n")

            ## Start plotter for visualization
            plotter = img_plotter.img_plotter(img_analyzer.sample_name, color_str=k_log.color_str)

            ## Sum three images at three positions
            if message['num_events']['primary']==3:
                print(f"\nStart to stitch {img_analyzer.run.start['sp_detector']} data: uid = {img_analyzer.uid}\n")
                img_analyzer.save_img_pilatus()
                print(f'\nApply mask {img_analyzer.stitched_mask = }\n')
                
            ## Process pe1c data without stitching 
            elif message['num_events']['primary']==1:
                print(f"\nStart to process {img_analyzer.run.start['detectors'][0]} data: uid = {img_analyzer.uid}\n")
                img_analyzer.save_img_perkin()
                print(f'\nApply mask {img_analyzer.mask_pe1c = }\n')
                
            ## Plot unmasked 2D image rings with histogram
            tiff3_tuner = plotter.plot_tiff3(img_analyzer.process_img, img_analyzer.mask_array, mask=False, histogram=True)
            tiff3_tuner()

            ## pyFai integration: 2D to 1D
            print(f"\nStart to do 2D integration: uid = {img_analyzer.uid}\n")
            iq_df, iq_fn, unrolled_array = img_analyzer.pct_integration()
            # img_tuner4 = plotter.plot_tiff4(unrolled_array, iq_df.iloc[:,0])
            
            ## Plot masked 2D image rings with iq data
            maskImg_iq_tuner = plotter.plot_maskImg_iq(img_analyzer.process_img,  
                                                        img_analyzer.mask_array, 
                                                        unrolled_array, 
                                                        iq_fn,
                                                        img_analyzer.poni_fn, 
                                                        )
            maskImg_iq_tuner()

            ## Plot masked and unrolled image cake
            # tiff4_tuner4 = plotter.plot_tiff4(unrolled_array, None, binned=True)
            # tiff4_tuner4()

            ## Data reduction: I(Q) to G(r)
            if (img_analyzer.do_reduction) and (img_analyzer.acq_mode()=='PDF'):
            # if img_analyzer.acq_mode=='PDF':
                print(f"\nStart to reduce sq, fq, gr: uid = {img_analyzer.uid}\n")
                # iq_array = iq_df.to_numpy().T
                sqfqgr_path = img_analyzer.get_gr(iq_df)
                bkg_scale = img_analyzer.pdfconfig().bgscale[0]
                bkg_fn = img_analyzer.pdfconfig_dict['backgroundfile']
                plotter.plot_sqfqgr(sqfqgr_path, bkg_scale, bkg_fn)
            
            else:
                print('This is an XRD scan. Skip gr transformation.')


            k_log.colo_str = plotter.color_str
            print('\n########### Events printing division ############\n')
      
           
        

    kafka_config = _read_bluesky_kafka_config_file(config_file_path="/etc/bluesky/kafka.yml")

    # this consumer should not be in a group with other consumers
    #   so generate a unique consumer group id for it
    unique_group_id = f"echo-{beamline_acronym_01}-{str(uuid.uuid4())[:8]}"

    kafka_consumer = BasicConsumer(
        topics=[f"{beamline_acronym_01}.bluesky.runengine.documents", 
                f"{beamline_acronym_02}.bluesky.runengine.documents"],
        bootstrap_servers=kafka_config["bootstrap_servers"],
        group_id=unique_group_id,
        consumer_config=kafka_config["runengine_producer_config"],
        process_message = print_message,
    )

    try:
        kafka_consumer.start_polling(work_during_wait=lambda : plt.pause(.1))
    except KeyboardInterrupt:
        print('\nExiting Kafka consumer')
        return()


if __name__ == "__main__":
    import sys
    print_kafka_messages(sys.argv[1], sys.argv[2])
