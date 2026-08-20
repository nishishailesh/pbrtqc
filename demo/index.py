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
import mysql_user as mysql_user
my_db='clg'
my_host='127.0.0.1'


#touch /var/log/CP.log
#chown www-data:www-data /var/log/CP.log
logging.basicConfig(filename="/var/log/CP.log",level=logging.DEBUG)
logging.debug("demo index:{}".format(sys.path))

#This file is in root folder, 
#wsgi.py have --> sys.path.append('/usr/share/nchs/cp')
#It accesible to all subfolders because wsgi alters path  
from verify_user import decorate_verify_user

@route('/demo/welcome', method='POST')
@decorate_verify_user    
def welcome():
  uname=request.forms.get("uname")
  psw=request.forms.get("psw")
  logging.debug("inside welcome......")
  return template("demo/welcome.html",uname=uname,psw=psw)
  #return "/start is reached"


