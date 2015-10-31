"""
Routines for configuring Samsara
"""
from __future__ import print_function
import logging as sys_logging
import os
import sys
import simplejson as json

#from oslo_concurrency import processutils
from oslo_config import cfg
#from oslo_log import log as logging

import config
from authenticate import get_nova_auth as nova_session


#LOG = logging.getLogger(__name__)

database_group = cfg.OptGroup('database')
database_opts = [cfg.StrOpt('connection', default='ddddd',help=("Connection to Database"))]
    
CONF = cfg.CONF

CONF.register_group(database_group)
CONF.register_opts(database_opts, database_group)

def main():
    config.parse_args(sys.argv)
    print('(simple) enable: {}'.format(CONF.database.connection ))
    nova = nova_session()
    print(nova.servers.list(detailed=True))  
    print(type(nova.hosts.list()))
    hosts_list = nova.hosts.list_all()
    for h in hosts_list:
      try:
        hostname = str(h.host_name)
        print ('Try to get system info from: ' + hostname)
        host_info = nova.hosts.get(hostname)
        #print(dir(host_info))
        # for hi in host_info:
#             print(type(hi))
#             print (dir(hi))
#             print (" {0} : {1} ".format(hi.project, hi.memory_mb))
        while True:
            print (str(host_info.pop().to_dict()))
      except Exception as e:
          print(e)