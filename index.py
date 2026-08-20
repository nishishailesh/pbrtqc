#!/usr/bin/python3
#from bottle import route, run, template
from bottle import template, request, post, route, redirect, TEMPLATE_PATH, response
from mysql_lis import mysql_lis
import sys, logging, bcrypt, csv, pprint, os, json
from functools import wraps
from io import StringIO


from bottle import static_file
@route('/bs')
def server_static():
    return static_file("/bootstrap/css/bootstrap.min.css", root='/usr/share/nchs/cp/')
    
    
#For mysql password, declared in wsgi.py
#sys.path.append('/var/mysql_user_for_python3')
###########Setup this for getting database,user,pass for HLA database##########
#This file is in root folder, 
#wsgi.py have --> sys.path.append('/usr/share/nchs/cp')
#It accesible to all subfolders because wsgi alters path 
import mysql_user as mysql_user
my_db='clg'
my_host='127.0.0.1'
##############################################################


#touch /var/log/CP.log
#chown www-data:www-data /var/log/CP.log
logging.basicConfig(filename="/var/log/CP.log",level=logging.DEBUG)  
logging.debug("cp index:{}".format(sys.path))

#This file is in root folder, 
#wsgi.py have --> sys.path.append('/usr/share/nchs/cp')
#It accesible to all subfolders because wsgi alters path
from verify_user import decorate_verify_user

#login page
@route('/')
def index():
  logging.debug("/ inside......")
  return template("index.html")
    

#This page have links to all sub-projects
@route('/start', method='POST')
@decorate_verify_user    
def start():
  uname=request.forms.get("uname")
  psw=request.forms.get("psw")
  logging.debug("START inside......")
  return template("initial_page.html",uname=uname,psw=psw)
  #return "/start is reached"


#one sub-project
#import its index (or whatever it's name)
import demo.index
#path-like usl is not essential. It could be simply demo
@route('/demo/start', method='POST')
@decorate_verify_user    
def demo():
  uname=request.forms.get("uname")
  psw=request.forms.get("psw")
  logging.debug("inside demo......")
  return template("demo/initial_page.html",uname=uname,psw=psw)

#XbarB sub-project
#import its index (or whatever it's name)
import xbarb.index
#path-like url is not essential. It could be anything
@route('/xbarb/start', method='POST')
@decorate_verify_user    
def xbarb_start():
  uname=request.forms.get("uname")
  psw=request.forms.get("psw")
  logging.debug("inside xbarb starto......")
  return template("xbarb/initial_page.html",uname=uname,psw=psw)
  
  
  
