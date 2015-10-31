"""
Routines for configuring Samsara
"""
from __future__ import print_function
import logging as sys_logging
import os
import sys

#from oslo_concurrency import processutils
from oslo_config import cfg
#from oslo_log import log as logging

import config
from credentials import get_nova_session as nova


#LOG = logging.getLogger(__name__)

database_group = cfg.OptGroup('database')
database_opts = [cfg.StrOpt('connection', default='ddddd',help=("Connection to Database"))]
    
CONF = cfg.CONF

CONF.register_group(database_group)
CONF.register_opts(database_opts, database_group)

def main():
    config.parse_args(sys.argv)
    print('(simple) enable: {}'.format(CONF.database.connection ))