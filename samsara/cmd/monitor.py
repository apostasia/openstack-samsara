#! /usr/bin/python
"""

Monitor System

"""
from __future__ import print_function
import logging
import os
import sys

sys.path.append('/home/vagrant/samsara')

#from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log
import oslo_messaging as messaging
from oslo_reports import guru_meditation_report as gmr

#from authenticate import get_nova_auth as nova_session

from samsara.common import config
from samsara.common import rpc

from samsara.monitor import monitor
from samsara import version


        
if __name__ == "__main__":
    sys.exit(monitor.main(sys.argv)) 