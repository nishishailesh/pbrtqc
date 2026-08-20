#!/usr/bin/python3
#from bottle import route, run, template
from bottle import template, request, post, route, redirect, TEMPLATE_PATH, response
from mysql_lis import mysql_lis
import sys, logging, bcrypt, csv, pprint, os, json
from functools import wraps
from io import StringIO

#For mysql password
sys.path.append('/var/mysql_user_for_python3')
###########Setup this for getting database,user,pass for HLA database##########
import mysql_user as mysql_user
my_db='clg'
my_host='127.0.0.1'
login_page_info="Login for NCHSLS Biochemistry Laboratory"
##############################################################
#touch /var/log/CP.log
#chown www-data:www-data /var/log/CP.log
logging.basicConfig(filename="/var/log/CP.log",level=logging.DEBUG)  


def verify_user():
  if(request.forms.get("uname")!=None and request.forms.get("psw")!=None):
    uname=request.forms.get("uname")
    psw=request.forms.get("psw")
    logging.debug('username and password are provided')
    logging.debug('username is:{}'.format(uname))
    m=mysql_lis(my_host,mysql_user.my_user,mysql_user.my_pass,my_db)
    m.run_query(prepared_sql='select * from user where user=%s',data_tpl=(uname,))
    user_info=m.get_single_row()
    logging.debug('user info'.format(user_info))
    if(user_info==None):
      logging.debug('user {} not found'.format(uname))
      m.close_cursor()
      m.close_link()
      return False
    m.close_cursor()
    m.close_link()

    '''
    Python: bcrypt.hashpw(b'mypassword',bcrypt.gensalt(rounds= 4,prefix = b'2b')
    PHP:    password_hash('mypassword',PASSWORD_BCRYPT);

    Python:bcrypt.checkpw(b'text',b'bcrypted password')
    PHP: password_verify('text,'bcrypted password')
    '''
    
    #try is required to cache NoneType exception when supplied hash is not bcrypt
    try:
      if(bcrypt.checkpw(psw.encode("UTF-8"),user_info[2].encode("UTF-8"))==True):
        logging.debug('user {}: password verification successful'.format(uname))
        return True
      else:
        return False
    except Exception as ex:
      logging.debug('{}'.format(ex))
      return False
  else:
    logging.debug("verify_user(): else reached, no uname psw found in request")
    return False
    
def decorate_verify_user(fun):
  def nothing():
    logging.debug("username/password not supplied/verified") 
    return "username/password not supplied/verified"  #this will be html output  because it will exit here
  @wraps(fun)   #not essential
  def do_it():
    if(verify_user()==True):
      logging.debug("#fun() reached...")
      return fun()  #return essential to return template
      #output of fun()[its template etc] will be html output  because it will exit here
    else:
      return nothing() #return essential to return template
  logging.debug("decorate_verify_user(fun):function name of do_it is {}".format(do_it.__name__))
  return do_it
