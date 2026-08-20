#!/usr/bin/python3
#from bottle import route, run, template
from bottle import template, request, post, route, redirect, TEMPLATE_PATH
from mysql_lis import mysql_lis
import sys, logging, bcrypt, csv, pprint, os
from functools import wraps
from io import StringIO

#####################################
#This is subproject.
#No need for login related activity
#####################################

#For mysql password
#This file is in root folder, 
#wsgi.py have --> sys.path.append('/usr/share/nchs/cp')
#It accesible to all subfolders because wsgi alters path
#path already declared in wsgi.py. But, not available here
#sys.path.append('/var/mysql_user_for_python3') 
import mysql_user as mysql_user

#This is alternate to sys.path.append
from . import pbrtqc #because bottle do not assume any module from current folder unless sys.path.append is used

my_db='clg'
my_host='127.0.0.1'


#touch /var/log/CP.log
#chown www-data:www-data /var/log/CP.log
logging.basicConfig(filename="/var/log/CP.log",level=logging.DEBUG)
logging.debug("xbarb index:{}".format(sys.path))
#This file is in root folder, 
#wsgi.py have --> sys.path.append('/usr/share/nchs/cp')
#It accesible to all subfolders because wsgi alters path  
from verify_user import decorate_verify_user

@route('/xbarb/show_data', method='POST')
@decorate_verify_user    
def show_data():
  uname=request.forms.get("uname")
  psw=request.forms.get("psw")
  
  limit=request.forms.get("limit")
  offset=request.forms.get("offset")
  binsize=request.forms.get("binsize")
  examination_id=request.forms.get("examination_id")
  
  parameters={'uname':uname,'psw':psw,'limit':int(limit), 'offset':int(offset) ,'binsize':int(binsize),'examination_id':int(examination_id)}
  logging.debug("inside xbarb show_data......")
  ms=mysql_lis(my_host,mysql_user.my_user,mysql_user.my_pass,my_db)
  r=pbrtqc.get_results(ms,examination_id,limit,offset)
  batch1=pbrtqc.get_bin_from_primary_result(r,20,0)
  batch2=pbrtqc.get_bin_from_primary_result(r,20,20)
  xb1=pbrtqc.get_new_xbarb(0,batch1)
  xb2=pbrtqc.get_new_xbarb(0,batch2)
  logging.debug(xb1)
  logging.debug(xb2)
  return template("xbarb/show_data.html",parameters=parameters,r=r,batch1=batch1,batch2=batch2)
  #return "/start is reached"


