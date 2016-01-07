#! /usr/bin/python
"""
Collector information About Hosts and Virtual Machines
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
from samsara.drivers import virt

from samsara.objects import base as objects_base
from samsara import version


collector_group = cfg.OptGroup ('collector')
collector_opts  = [cfg.IntOpt('interval', default=30,
                                          help=("Interval between collects (in seconds)"))]    
CONF = cfg.CONF

CONF.register_group(collector_group)
CONF.register_opts(collector_opts, collector_group)

virt_driver      = virt.LibvirtDriver()

# LOG
log.register_options(CONF)
CONF.set_override('log_file', '/var/log/samsara/samsara-collector.log')
log.setup(CONF, 'samsara-collector')
LOG = log.getLogger('samsara-collector')

# Notify
transport_url = 'rabbit://samsara:samsara@localhost:5672/'
transport = messaging.get_transport(cfg.CONF, transport_url)
driver = 'messaging'
# notifier = messaging.Notifier(transport, driver=driver, publisher_id='samsara', topic='collector')

#notifier = rpc.get_notifier()

def main():
    config.parse_args(sys.argv)
    
    ctx_repository = contexts_repository.LocalContextsRepository()
    serializer   = objects_base.SamsaraObjectSerializer()
    
    
    gmr.TextGuruMeditation.setup_autorun(version)
    
    while True:
        
        
        # Get Host Contexts
        ctx_host_resources_usage = contexts.HostResourceUtilization('host_resources_usage').getContext()
        ctx_repository.store_context(ctx_host_resources_usage)
        LOG.debug(ctx_host_resources_usage)
        LOG.info(ctx_repository.list_context_vars('host_resources_usage'))
        
        # notifier.info({'some': 'context'}, 'host.get_resources', 'ok')
        
        # Get Virtual Machine Contexts
        for vm_id in virt_driver.get_active_instacesID():
            ctx_vm_resources_usage = contexts.VirtualMachineResourceUtilization('vm_resources_usage',vm_id).getContext()
            ctx_repository.store_context(ctx_vm_resources_usage)
        
        LOG.info('Collect Contexts: OK')
        
        # Update vcpu_time for all instances
        virt_driver.update_vcpu_time_instances()
        LOG.info('Update VCPU time for all instances')

        #### Delay for 15 seconds ####
        time.sleep(CONF.collector.interval)
        
if __name__ == "__main__":
    sys.exit(main()) 