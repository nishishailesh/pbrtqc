#!/usr/bin/python3

import sys, io
import logging
import time
import zlib
import base64
import struct
import decimal
import base64 

#apt search python3-matplotlib
#apt install python3-matplotlib
#import matplotlib.pyplot as plt 
import numpy as np 
#import pandas as pd

import datetime

from mysql_lis import mysql_lis

#to ensure that password is not in main sources
#prototype file is as follows

'''
example /var/gmcs_config/astm_var.py
#!/usr/bin/python3.7
my_user='uuu'
my_pass='ppp'
'''

'''
if anything is redirected, last newline is added.
To prevent it, use following
I needed this while outputting relevant data to a file via stdout redirection
echo -n `./astm_file2mysql_general.py` > x
'''

#log_filename='/var/log/mylog/all_ma.log'
#logging.basicConfig(filename=log_filename,level=logging.DEBUG)
#logging.basicConfig(filename=log_filename,level=logging.debug)
#logging.debug(sys.argv)

#sys.path.append('/var/gmcs_config')
#import astm_var

#print(dir(astm_var))
#n_size=sys.argv[1]
#o_size=sys.argv[2]
#ex_id=sys.argv[3]
#mean_mean=None
#mean_sd=None
#finall=None
#finall_with_result=None
#Globals for configuration################
#used by parent class astm_file (so be careful, they are must)

#log=1
#my_host='127.0.0.1'
#my_user=astm_var.my_user
#my_pass=astm_var.my_pass
#my_db='clg'


#if log==0:
#  logging.disable(logging.CRITICAL)


def decode_base64_and_inflate( b64string ):
    decoded_data = base64.b64decode( b64string )
    return zlib.decompress( decoded_data , -15)

#not used in this project
def deflate_and_base64_encode( string_val ):
    zlibbed_str = zlib.compress( string_val )
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode( compressed_string )


def mk_histogram_from_tuple(xy):
  global mean_mean
  global mean_sd
  global n_size
  global finall
  global finall_with_result
  #xy[0] will be used as datgaframe raw lable
  r=pd.DataFrame(xy[1],xy[0])
  m=r.rolling(20).mean()
  md=r.rolling(20).median()
  #ewma=r.ew
  
  rr=r.rename(columns={0:"result"})
  mm=m.rename(columns={0:"avg(20)"})
  mdd=md.rename(columns={0:"median(20)"})
  
  
  #final=rr.join(mm)
  #finall=final.join(mdd)
  
  finall=mm.join(mdd)
  finall_with_result=finall.join(r)
  finall_with_result.columns = ['mean(20)','median(20)','actual result']

  logging.debug(finall)

  mean_sd=m.std()
  mean_mean=m.mean()
  logging.debug('mean_sd={}:mean_mean={}'.format(mean_sd,mean_mean))
  finall.plot(figsize=(26,8),subplots=False)
  plt.plot([ xy[3],xy[2] ],[mean_mean,mean_mean])
  plt.ticklabel_format(style='plain')

  
  plt.plot([ xy[3],xy[2] ],[mean_mean+mean_sd,mean_mean+mean_sd])
  plt.plot([ xy[3],xy[2] ],[mean_mean-mean_sd,mean_mean-mean_sd])

  plt.plot([ xy[3],xy[2] ],[mean_mean+mean_sd*2,mean_mean+mean_sd*2])
  plt.plot([ xy[3],xy[2] ],[mean_mean-mean_sd*2,mean_mean-mean_sd*2])

  plt.plot([ xy[3],xy[2] ],[mean_mean+mean_sd*3,mean_mean+mean_sd*3])
  plt.plot([ xy[3],xy[2] ],[mean_mean-mean_sd*3,mean_mean-mean_sd*3])

  #plt.yticks (ticks=np.linspace(mean_mean-3*mean_sd,mean_mean+3*mean_sd,7))

  #finall.plot(figsize=(26,17),subplots=True)
  
  f = io.BytesIO()
  plt.savefig(f, format='png')
  f.seek(0)
  data=f.read()
  f.close()
  plt.close()	#otherwise graphs will be overwritten, in next loop
  return data


def get_results(ms,examination_id,n_size,o_size):
  prepared_sql='select * from primary_result where examination_id=%s and result>0 order by sample_id desc limit %s offset %s'
  data_tpl=(int(examination_id),int(n_size),int(o_size))
  logging.debug(data_tpl)
  ms.run_query(prepared_sql,data_tpl)
  logging.debug(prepared_sql)
  logging.debug(data_tpl)
  logging.debug("cur:{}".format(ms.cur))
  r=None
  if(ms.cur!=None):
    logging.debug("cur is not None")
    r=ms.get_all_rows()
  else:
    logging.debug("cur is None")
  return r


def get_batch(csv_stream,batch):
  batch_data=[]
  i=0
  while i < batch:
    row = next(c)
    try:
      primary_result=float(row[2])
      batch_data=batch_data+[primary_result]
      i=i+1
    except ValueError:
      pass    
  return batch_data





def get_bin_from_primary_result(primary_result,bin_size,offset):
  #(1019872, 5019, '135.19', None, '20260502103845|XL_1000')
  sample_id=[]
  examination_id=[]
  result=[]
  extra=[]
  uniq=[]
  
  i=0
  while i < bin_size:
    try:
      sample_id=sample_id+[primary_result[i+offset][0]]
      examination_id=examination_id+[primary_result[i+offset][1]]
      result=result+[primary_result[i+offset][2]]
      extra=extra+[primary_result[i+offset][3]]
      uniq=uniq+[primary_result[i+offset][4]]
      i=i+1
    except ValueError:
      pass    
  return [sample_id,examination_id,result,extra,uniq]
  
def clean_patient_result(data):
  fdata=[]
  for i in data:
    try:
      fdata=fdata+[float(i)]     
    except Exception as ex:
      pass
  logging.debug("RECEIVED data after cleaning:lenght is:{}:data:{}".format(len(fdata),fdata))
  return fdata
      
def get_new_xbarb(xbarb,batch_data):
  logging.debug("get_new_xbarb RECEIVED batch data:{}".format(batch_data))
  logging.debug("get_new_xbarb old xbarb:{}".format(xbarb))
  xbarb=np.float64(xbarb);
  logging.debug("get_new_xbarb np xbarb:{}".format(xbarb))
  fbatch_data=clean_patient_result(batch_data)
  np_batch_data=np.array(fbatch_data)
  logging.debug(np_batch_data)
  np_batch_data=np_batch_data.reshape(-1,1)
  zero=np.zeros((len(batch_data),1))
  logging.debug("\nZERO\n{}".format(zero))
  #find sign of result-xbarb
  np_batch_data=np.append(np_batch_data, zero,axis=1)
  logging.debug("\nnp_batch_data (zero colum added) \n{}".format(np_batch_data))
  np_batch_data[:, 1]=np.sign(np_batch_data[:, 0]-xbarb)
  logging.debug("\nnp_batch_data zero column converted to sign\n{}".format(np_batch_data))


  np_batch_data=np.append(np_batch_data, zero,axis=1)
  logging.debug("\nnp_batch_data (zero colum added)\n{}".format(np_batch_data))
  np_batch_data[:, 2]=abs(np_batch_data[:, 0]-xbarb)
  logging.debug("\nnp_batch_data zero column converted to abs \n{}".format(np_batch_data))
  np_batch_data=np.append(np_batch_data, zero,axis=1)
  logging.debug("\nnp_batch_data (zero colum added)\n{}".format(np_batch_data))
  np_batch_data[:, 3]=np.sqrt(np_batch_data[:, 2])
  logging.debug("\nnp_batch_data zero column converted to sqrt of abs \n{}".format(np_batch_data))


  np_batch_data=np.append(np_batch_data, zero,axis=1)
  logging.debug("\nnp_batch_data (zero colum added)\n{}".format(np_batch_data))
  np_batch_data[:, 4]=np_batch_data[:, 1]*np_batch_data[:, 3]
  logging.debug("\nnp_batch_data zero column converted sqrt*sign \n{}".format(np_batch_data))

  sum_of_signed_sqrt=sum(np_batch_data[:, 4])
  logging.debug("\nsum_of_signed_sqrt:{}".format(sum_of_signed_sqrt))
  sign_of_sum_of_signed_sqrt=np.sign(sum_of_signed_sqrt)
  logging.debug("\nsign_of_sum_of_signed_sqrt:{}".format(sign_of_sum_of_signed_sqrt))


  squre_of_avg_of_signed_sqrt=(sum_of_signed_sqrt/len(batch_data))**2
  logging.debug("\nsqure_of_avg_of_signed_sqrt:{}".format(squre_of_avg_of_signed_sqrt))

  d=sign_of_sum_of_signed_sqrt*squre_of_avg_of_signed_sqrt
  logging.debug("\nsigned batch delta xbarb:{}".format(d))

  new_xbarb=xbarb+d
  logging.debug("\nnew xbarb:{}".format(new_xbarb))
  
  return new_xbarb


def get_bin_results(ms,examination_id):
  ####### Find currenly valid reference data #############
  prepared_sql_ref='select * from xbarb_xxx_lab_reference_value where examination_id=%s'
  data_tpl=(int(examination_id),)
  logging.debug(data_tpl)
  logging.debug(prepared_sql_ref)
  ms.run_query_with_field_names(prepared_sql_ref,data_tpl)
  logging.debug("cur:{}".format(ms.cur))
  ref=ms.get_all_rows()
  if(ms.cur==None):
    logging.debug("cur is None. EXITING get_bin_results(ms,examination_id)")
    return false
  current_datetime=datetime.datetime.now()
  relevent_ref=[each_ref for  each_ref in ref if each_ref['start_datetime']<current_datetime<each_ref['end_datetime']]
  algo_list=[each_ref['algorithm'] for each_ref in relevent_ref]
  logging.debug("expected algorythms:{}".format(algo_list))
  
  ######### For each alogrithm, find last entry ############
  for each_relevent_ref in relevent_ref:
    logging.info("===================one reference management:{}".format(each_relevent_ref))    
    prepared_sql_r='select * from xbarb_primary_result where examination_id=%s and uniq=%s order by sample_id desc limit 1'
    data_tpl=(int(examination_id),each_relevent_ref['algorithm'])
    logging.debug(prepared_sql_r)
    logging.debug(data_tpl)
    ms.run_query_with_field_names(prepared_sql_r,data_tpl)
    logging.debug("cur:{}".format(ms.cur))
    last_entry=ms.get_single_row()
    logging.debug("last_entry for {}:{}".format(each_relevent_ref['algorithm'],last_entry))
    
    ###### Find examinations after last entry #####
    equipment_of_ref=each_relevent_ref['algorithm'].split('|')[0]
    logging.debug("equipment_of_ref:{}".format(equipment_of_ref))
    
    
    prepared_sql_pr='select * from primary_result where examination_id=%s and result REGEXP "^-?[0-9]+\\.[0-9]+$" and sample_id>%s \
            and substring_index(uniq,"|",-1)=%s limit %s'
    
    data_tpl=(
                int(examination_id),
                last_entry['sample_id'],
                equipment_of_ref,
                int(each_relevent_ref['bin_size'])
              )
              
    logging.debug(prepared_sql_pr)                
    logging.debug(data_tpl)
    ms.run_query_with_field_names(prepared_sql_pr,data_tpl)
    logging.debug("cur:{}".format(ms.cur))
    pr_list=ms.get_all_rows()
    total_results=len(pr_list)
    if(total_results>=int(each_relevent_ref['bin_size'])):
      logging.debug("total results avilable for calculation:{}".format(total_results))
      logging.debug("primary results for {}:{}".format(each_relevent_ref['algorithm'],pr_list))
      all_results=[one_data['result'] for one_data in pr_list]
      logging.debug("primary results :{}".format(all_results))
      logging.debug("primary result count:{}".format(total_results))
      if(each_relevent_ref['algorithm'].split("|")[1]=='xbarb'):
        calculated_xbarb=get_new_xbarb(last_entry['result'],all_results)
        logging.info("new xbarb:{}".format(calculated_xbarb))
        logging.info("primary result last sample details:{}".format(pr_list[total_results-1]))
        last_primary_sample_data=pr_list[total_results-1]
        data_tpl=(last_primary_sample_data['sample_id'],examination_id,calculated_xbarb,last_entry['uniq'])
        logging.info("data_tpl for new xbarb_primary_result is:{}".format(data_tpl))    
        prepared_sql_insert_new_xbarb='insert into xbarb_primary_result \
                                      (sample_id,examination_id,result,uniq)values \
                                      (%s,%s,%s,%s)'
        logging.info('prepared_sql_insert_new_xbarb:{}'.format(prepared_sql_insert_new_xbarb))
        ms.run_query_with_field_names(prepared_sql_insert_new_xbarb,data_tpl)
        logging.info("cur:{}".format(ms.cur))     
        
      elif(each_relevent_ref['algorithm'].split("|")[1]=='mean'):
        logging.info("mean algorithm is not implimented yet")    
    else:
      logging.debug("Better luck next time. total results avilable for calculation:{}<{}".format(total_results,each_relevent_ref['bin_size']))

  return True
   
    
'''
ms=my_sql()
ms.get_link(astm_var.my_host,astm_var.my_user,astm_var.my_pass,astm_var.my_db)

#examination_id=5031
examination_id=sys.argv[3]
x,y,h,m=get_results(ms,examination_id,int(n_size),int(o_size))
logging.debug((x,y,h,m))
data=mk_histogram_from_tuple((x,y,h,m))

encoded=base64.b64encode(bytes(data))

output=b''
output=output+b"<h4>Examination ID: "+bytes(   str(examination_id).encode('UTF-8')  )+b"</h4>"
output=output+b"<img width=1200 src='data:image/png;base64,"+ encoded +b"'/>"
output=output+b"<h4>mean of mean: "+bytes(str(round(mean_mean[0],2)).encode('UTF-8')) + b"<br>sd of mean:"+bytes(str(round(mean_sd[0],2)).encode('UTF-8'))+b"</h4>"
output=output+b"<h4>min sample id: "+ bytes(str(m).encode('UTF-8')) + b"<br>max Sample ID:"+bytes(str(h).encode('UTF-8'))+b"</h4>"
output=output+b"<h3>All data points, in reverse order</h3>"
#output=output+b"<pre>"+bytes( str(finall.head(100).to_string()).encode('UTF-8'))
output=output+b"<pre>"+bytes( str(finall_with_result.to_string()).encode('UTF-8'))

sys.stdout.buffer.write(output)
'''
