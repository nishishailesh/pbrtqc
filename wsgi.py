#!/usr/bin/python3
#this file is refered in apache2 conf
import os, sys, logging
# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))

#where scripts are stored
sys.path.append('/usr/share/nchs/cp')
#for username password of mysql access
sys.path.append('/var/mysql_user_for_python3') 
#logging.debug("wwwwwwwwwwwwwwwsgi:{}".format(sys.path))

#passed on main module
import bottle

#following in name of python file which will be accessed for routes
import index
# ... build or import your bottle application here ...
# Do NOT use bottle.run() with mod_wsgi
application = bottle.default_app()
