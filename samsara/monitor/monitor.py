#! /usr/bin/python
# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""
Monitor Service
"""
from __future__ import print_function
import logging
import os
import sys
import time
from datetime import datetime
import simplejson as json
import psutil

sys.path.append('/home/vagrant/samsara')

#from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log
import oslo_messaging as messaging
from oslo_reports import guru_meditation_report as gmr

#from authenticate import get_nova_auth as nova_session

from samsara.common import config
from samsara.common import rpc

from samsara.context_aware import entities
from samsara.context_aware import sensors
from samsara.context_aware import contexts
from samsara.context_aware import contexts_repository

from samsara.objects import base as objects_base
from samsara import version


monitor_group = cfg.OptGroup ('monitor')
monitor_opts  = [cfg.IntOpt('interval', default=30,
                                          help=("Interval between collects (in seconds)"))]    
CONF = cfg.CONF

CONF.register_group(monitor_group)
CONF.register_opts(monitor_opts, monitor_group)

# LOG
log.register_options(CONF)
CONF.set_override('log_file', '/var/log/samsara/samsara-monitor.log')
log.setup(CONF, 'samsara-monitor')
LOG = log.getLogger('samsara-monitor')

# Notify
transport_url = 'rabbit://samsara:samsara@localhost:5672/'
transport = messaging.get_transport(cfg.CONF, transport_url)
driver = 'messaging'
# notifier = messaging.Notifier(transport, driver=driver, publisher_id='samsara', topic='monitor')

#notifier = rpc.get_notifier()

def main(argv):
    config.parse_args(argv)
    
    ctx_repository = contexts_repository.LocalContextsRepository()
    serializer   = objects_base.SamsaraObjectSerializer()
    gmr.TextGuruMeditation.setup_autorun(version)
    
    while True:
        
        # Get Host Contexts from COntexts Repository
        for last_ctx in ctx_repository.retrieve_last_n_contexts('host_resources_usage', 2):
            LOG.info(last_ctx['created_at'])
        # notifier.info({'some': 'context'}, 'host.get_resources', 'ok')
        
        #### Delay for 15 seconds ####
        time.sleep(CONF.monitor.interval)
        
if __name__ == "__main__":
    sys.exit(main()) 