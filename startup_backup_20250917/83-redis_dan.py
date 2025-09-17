import redis, ast, json


redis_host = 'info.pdf.nsls2.bnl.gov'

rkvs = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

my_config = {'auto_mask': False,
    'user_mask': '/nsls2/data/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/my_mask_xrd3.npy',
    'method': 'splitpixel'} 


def convert_1d_nparray_to_json(x):
    if type(x) is np.ndarray:
        xlist = x.tolist()
    elif type(x) is list:
        xlist = x
    else:
        print ("unknown type")
    json_x = json.dumps(xlist)
    return json_x


def rkvs_keys(printed=True):
    '''Convert rkvs.keys() into a list of normal strings
    With printed=True, write a table of keys and values to the screen
    With printed=False, return a list containing keys as normal strings
    '''
    keys = sorted(list(x.decode('UTF-8') for x in rkvs.keys()))
    if printed is True:
        for k in keys:
            if rkvs.type(k) == b'string':
                print(f'{k:25} {rkvs.get(k).decode("UTF-8")}')
            elif rkvs.type(k) == b'list':
                this = ' '.join(x.decode('UTF-8') for x in rkvs.lrange(k, 0, -1))
                print(f'{k:25} {this}')
            else:
                #print(f'{k:25} {rkvs.get(k)}')
                pass
        return()
    else:
        return(keys)

def read_index_data_smart(filename,junk=None,backjunk=None,splitchar=None, do_not_float=False, shh=True, use_idex=[0,1]):
    with open(filename,'r',encoding="utf8") as infile:
        datain = infile.readlines()
    
    if junk == None:
        for i in range(len(datain)):
            try:
                for j in range(10):
                    x1,y1 = float(datain[i+j].split(splitchar)[use_idex[0]]), float(datain[i+j].split(splitchar)[use_idex[1]])
                junk = i
                break
            except:
                pass #print ('nope')
                
    if backjunk == None:
        for i in range(len(datain),-1,-1):
            try:
                x1,y1 = float(datain[i].split(splitchar)[use_idex[0]]), float(datain[i].split(splitchar)[use_idex[1]])
                backjunk = len(datain)-i-1
                break
            except:
                pass
                #print ('nope')
    
    if backjunk == 0:
        datain = datain[junk:]
    else:
        datain = datain[junk:-backjunk]
    
    xin = np.zeros(len(datain))
    yin = np.zeros(len(datain))
    
    if do_not_float:
        xin = []
        yin = []
    
    if shh == False:
        print ('length '+str(len(xin)))
    if do_not_float:
        if splitchar==None:
            for i in range(len(datain)):
                xin.append(datain[i].split()[use_idex[0]])
                yin.append(datain[i].split()[use_idex[1]])
        else:
            for i in range(len(datain)):
                xin.append(datain[i].split(splitchar)[use_idex[0]])
                yin.append(datain[i].split(splitchar)[use_idex[1]])    
    else:        
        if splitchar==None:
            for i in range(len(datain)):
                xin[i]= float(datain[i].split()[use_idex[0]])
                yin[i]= float(datain[i].split()[use_idex[1]])
        else:
            for i in range(len(datain)):
                xin[i]= float(datain[i].split(splitchar)[use_idex[0]])
                yin[i]= float(datain[i].split(splitchar)[use_idex[1]])   
        
    return xin,yin    



def stow_background(x, y):
    rkvs.set('PDF:bgd:x',str(list(x)))
    rkvs.set('PDF:bgd:y',str(list(y)))

def retrieve_background():
    x = ast.literal_eval(rkvs.get('PDF:bgd:x').decode('utf-8'))
    y = ast.literal_eval(rkvs.get('PDF:bgd:y').decode('utf-8'))
    return x,y

def stow_sample_number(sample_num):
    rkvs.set('PDF:xpdacq:sample_number', sample_num)

def retrieve_sample_number():
    return int(rkvs.get('PDF:xpdacq:sample_number').decode('utf-8'))

def stow_exposure_time(exposure_time):
    rkvs.set('PDF:desired_exposure_time',exposure_time)

def retrieve_exposure_time():
    return float(rkvs.get('PDF:desired_exposure_time').decode('utf-8'))

#def stow_sample_info(sample_num):
#    info =dict(bt.samples[list(bt.samples.keys())[sample_num]])
#    j_info = json.dumps(info)
#    rkvs.set('PDF:xpdacq:sample_info',j_info)

#def retrieve_sample_info():
#    j_info = rkvs.get('PDF:xpdacq:sample_info')
#    return json.loads(j_info)

#def stow_scanplan_num(scanplan_num):
#    rkvs.set('PDF:xpdacq:scanplan_num', scanplan_num)

#def retrieve_scanplan_num():
#    return int(rkvs.get('PDF:xpdacq:scanplan_num').decode('utf-8'))


def stow_recent_shifter_scan(x,y):
    xjson = convert_1d_nparray_to_json(x)
    yjson = convert_1d_nparray_to_json(y)
    rkvs.set('PDF:scan_shifter_pos:x',xjson)
    rkvs.set('PDF:scan_shifter_pos:y',yjson)
    
def retrieve_recent_shifter_scan():
    xjson = rkvs.get('PDF:scan_shifter_pos:x')
    yjson = rkvs.get('PDF:scan_shifter_pos:y')
    x = np.array(json.loads(xjson))
    y = np.array(json.loads(yjson))
    return x,y 


def stow_bt_sample_info():
   all_sample_names = list(bt.samples)
   big_dict = {}
   for this in all_sample_names:
       mini_dict = dict(bt.samples[this])
       big_dict[this] = mini_dict
   j_sample_dict = json.dumps(big_dict)
   rkvs.set('PDF:xpdacq:sample_dict', j_sample_dict)

#def retrieve_bt_sample_info():
#   j_sample_dict = rkvs.get('PDF:xpdacq:sample_dict')
#   return json.loads(j_sample_dict)

#def save_background_from_redis(output_file):
#    """ provide path for csv output_file (e.g. background.csv') """
#    xb, yb = retrieve_background()
#    pd.DataFrame(zip(np.array(xb), np.array(yb))).to_csv(output_file, header=None, index=None)
#
#def read_background_csv_into_redis(background_file, return_bgd = False):
#    xb, yb = pd.read_csv(background_file,index_col=None,header=None)
#    stow_background(xb, yb)
#    if return_bgd:
#        return xb, yb

def stow_Det_1_Z_near(near_coord):
    rkvs.set('PDF:bl_config:Det_1_Z:near',near_coord)

def stow_Det_1_Z_far(far_coord):
    rkvs.set('PDF:bl_config:Det_1_Z:far',far_coord)


def retrieve_Det_1_Z_near():
    return float(rkvs.get('PDF:bl_config:Det_1_Z:near').decode('utf-8'))
    
def retrieve_Det_1_Z_far():
    return float(rkvs.get('PDF:bl_config:Det_1_Z:far').decode('utf-8'))
    
def stow_pdfstream_config_near(my_config):
    p_my_config = json.dumps(my_config)
    rkvs.set('PDF:xpdacq:user_config:near',p_my_config)

def retrieve_pdfstream_config_near():
    p_my_config = rkvs.get('PDF:xpdacq:user_config:near')
    return json.loads(p_my_config)

def stow_pdfstream_config_far(my_config):
    p_my_config = json.dumps(my_config)
    rkvs.set('PDF:xpdacq:user_config:far',p_my_config)

def retrieve_pdfstream_config_far():
    p_my_config = rkvs.get('PDF:xpdacq:user_config:far')
    return json.loads(p_my_config)


def retrieve_pdfstream_pdfCalib():
    p_info = rkvs.get('PDF:xpdacq:pdf_calibration_md')
    return json.loads(p_info)
def retrieve_pdfstream_xrdCalib():
    p_info = rkvs.get('PDF:xpdacq:xrd_calibration_md')
    return json.loads(p_info)

def stow_pdfstream_xrdCalib(xrd_calib):
    p_my_calib = json.dumps(xrd_calib)
    rkvs.set('PDF:xpdacq:xrd_calibration_md',p_my_calib)
def stow_pdfstream_pdfCalib(pdf_calib):
    p_my_calib = json.dumps(pdf_calib)
    rkvs.set('PDF:xpdacq:pdf_calibration_md',p_my_calib)

def stow_beamtime_info(proposal_num, saf_num, session_num=0):
    rkvs.set('PDF:bt_info:proposal_id', proposal_num)
    rkvs.set('PDF:bt_info:data_session', 'pass-'+str(proposal_num))
    rkvs.set('PDF:bt_info:saf_id', saf_num)
    rkvs.set('PDF:bt_info:session_id',session_num)

def retrieve_beamtime_info():
    try:
        proposal_num = int(rkvs.get('PDF:bt_info:proposal_id'))
        saf_num = int(rkvs.get('PDF:bt_info:saf_id'))
        session_num = int(rkvs.get('PDF:bt_info:session_id'))
        this_dict = {}
        this_dict['data_session'] = proposal_num
        this_dict['saf_id'] = saf_num
        this_dict['session_id'] = session_num
        return this_dict

    except:
        print ('problem retrieving beamtime info')
        return None

#def stow_xrd_sample_number(sample_num):
#    rkvs.set('PDF:xpdacq:xrd_sample_number', sample_num)
    
#def stow_pdf_sample_number(sample_num):
#    rkvs.set('PDF:xpdacq:pdf_sample_number', sample_num)

#def retrieve_pdf_sample_number():
#    return int(rkvs.get('PDF:xpdacq:pdf_sample_number').decode('utf-8'))

#def retrieve_xrd_sample_number():
#    return int(rkvs.get('PDF:xpdacq:xrd_sample_number').decode('utf-8'))
