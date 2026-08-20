#!/usr/bin/python3
from  matplotlib import pyplot as plt
import csv,sys
import scipy.signal as sig
import pprint
import numpy as np
from numpy import trapz
import math
'''
csv_reader = reader(iterable [, dialect='excel']
            [optional keyword args])
  for row in csv_reader:
    process(row)
'''

#f=open("peak.csv","r")
f=open(sys.argv[1],"r")
c=csv.reader(f)
#c is file like. needs reload or rewind once read

#initial Xbarv
xbarb=4.41

#batch size to find new xbarb
batch=20

xbarb_array=[]

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
  

def get_new_xbarb(xbarb,batch_data):
  np_batch_data=np.array(batch_data)
  np_batch_data=np_batch_data.reshape(-1,1)
  zero=np.zeros((20,1))

  #find sign of result-xbarb
  np_batch_data=np.append(np_batch_data, zero,axis=1)
  #print(np_batch_data)
  np_batch_data[:, 1]=np.sign(np_batch_data[:, 0]-xbarb)
  #print(np_batch_data)


  np_batch_data=np.append(np_batch_data, zero,axis=1)
  #print(np_batch_data)
  np_batch_data[:, 2]=abs(np_batch_data[:, 0]-xbarb)
  np_batch_data[:, 2]=np.sqrt(np_batch_data[:, 2])
  #print(np_batch_data)


  np_batch_data=np.append(np_batch_data, zero,axis=1)
  #print(np_batch_data)
  np_batch_data[:, 3]=np_batch_data[:, 1]*np_batch_data[:, 2]
  #print(np_batch_data)

  sum_of_signed_sqrt=sum(np_batch_data[:, 3])
  #print(sum_of_signed_sqrt)

  sign_of_sum_of_signed_sqrt=np.sign(sum_of_signed_sqrt)
  #print(sign_of_sum_of_signed_sqrt)


  squre_of_avg_of_signed_sqrt=(sum_of_signed_sqrt/batch)**2
  #print(squre_of_avg_of_signed_sqrt)

  d=sign_of_sum_of_signed_sqrt*squre_of_avg_of_signed_sqrt
  #print(d)

  new_xbarb=xbarb+d
  print("new xbarb={}".format(new_xbarb))
  return new_xbarb


for i in range(0,300):
  batch_data=get_batch(c,batch)
  xbarb=get_new_xbarb(xbarb,batch_data)
  xbarb_array=xbarb_array+[xbarb]

print(xbarb_array)
print(np.std(xbarb_array))
print(np.mean(xbarb_array))
std=float(np.std(xbarb_array))
mean=float(np.mean(xbarb_array))

plt.plot(range(0,len(xbarb_array)),xbarb_array)
plt.plot([0,len(xbarb_array)],[mean+3*std,mean+3*std])
plt.plot([0,len(xbarb_array)],[mean,mean])
plt.plot([0,len(xbarb_array)],[mean-3*std,mean-3*std])



plt.yticks(np.arange(mean-5*std,mean+5*std,std))
plt.show()
plt.close() #otherwise graphs will be overwritten, in next loop
quit()
