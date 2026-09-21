#!/usr/bin/python3

import sys, io
import logging
import time
import zlib
import base64
import struct
import decimal
import base64 
import json
#apt search python3-matplotlib
#apt install python3-matplotlib
#import matplotlib.pyplot as plt 
import numpy as np 
#import pandas as pd

import datetime

from mysql_lis import mysql_lis

#this is just a module.
#logging is handled by calling file

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
  prepared_sql_ref='select * from current_xbarb_xxx_lab_reference_value where examination_id=%s'
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
  relevent_ref=ref
  algo_list=[each_ref['algorithm'] for each_ref in relevent_ref]
  logging.debug("expected algorithms:{}".format(algo_list))
  
  ######### For each alogrithm, find last entry ############
  # 20250122214139
  # 2025 01 22 21 41 39 
  # YYYY MM DD HH MM SS
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
    
    
    prepared_sql_pr='select * from primary_result where \
                      examination_id                  =%s                           and \
                      result                          REGEXP "^-?[0-9]+\\.[0-9]+$"  and \
                      substring_index(uniq,"|",1)     >%s                           and \
                      substring_index(uniq,"|",-1)    =%s                               \
                      order by substring_index(uniq,"|",1)                              \
                      limit %s'
    
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
      #all_sample_id=[one_data['sample_id'] for one_data in pr_list]
      #logging.debug("primary results sample_id:{}".format(all_sample_id))
      logging.debug("primary results :{}".format(all_results))

      #all_result_pairs=[ [ one_data['sample_id'], one_data['result'], one_data['uniq'] ] for one_data in pr_list]
      #logging.debug("primary results pairs:{}".format(all_result_pairs))
      
      pr_list_json=json.dumps(pr_list)[0:4000]
      logging.debug("pr_list JSON:{}".format(pr_list_json))
      logging.debug("primary result count:{}".format(total_results))
      
      if(each_relevent_ref['algorithm'].split("|")[1]=='xbarb'):
        calculated_xbarb=get_new_xbarb(last_entry['result'],all_results)
        logging.info("new xbarb:{}".format(calculated_xbarb))
        logging.info("primary result last sample details:{}".format(pr_list[total_results-1]))
        last_primary_sample_data=pr_list[total_results-1]
        smaple_id_for_xbarb_primary_result=last_primary_sample_data['uniq'].split("|")[0]
        data_tpl=(smaple_id_for_xbarb_primary_result, examination_id,calculated_xbarb,pr_list_json,last_entry['uniq'])
        logging.info("data_tpl for new xbarb_primary_result is:{}".format(data_tpl))    
        prepared_sql_insert_new_xbarb='insert into xbarb_primary_result \
                                      (sample_id,examination_id,result,extra,uniq) \
                                      values \
                                      (%s,%s,%s,%s,%s)'
        logging.info('prepared_sql_insert_new_xbarb:{}'.format(prepared_sql_insert_new_xbarb))
        ms.run_query_with_field_names(prepared_sql_insert_new_xbarb,data_tpl)
        logging.info("cur:{}".format(ms.cur))     
        
      elif(each_relevent_ref['algorithm'].split("|")[1]=='mean'):
        logging.info("mean algorithm is not implimented yet")    
    else:
      logging.debug("Better luck next time. total results avilable for calculation:{}:{}<{}".format(each_relevent_ref['algorithm'],total_results,each_relevent_ref['bin_size']))

  return True
