#!/usr/bin/python3

from mysql_lis import mysql_lis
import sys, logging, bcrypt, pprint, os

sys.path.append('/var/gmcs_config')
import astm_var_clg as astm_var

import pbrtqc 

logging.basicConfig(filename="/var/log/pbrtqc.log",level=logging.DEBUG)
#logging.basicConfig(filename="/var/log/pbrtqc.log",level=logging.INFO)


ms=mysql_lis(astm_var.my_host, astm_var.my_user, astm_var.my_pass, astm_var.my_db)
r=pbrtqc.get_bin_results(ms,5020)
logging.debug(r)
#r=pbrtqc.get_bin_results(ms,5020)
#logging.debug(list(r))


