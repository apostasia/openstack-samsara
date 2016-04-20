# Copyright (c) 2010 OpenStack Foundation
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Samsara Collector Manager
"""

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_serialization import jsonutils
from oslo_service import periodic_task
from oslo_utils import importutils

#from samsara.common import config
#from samsara.common import exception
from samsara.common import manager

from samsara.context_aware import entities
from samsara.context_aware import sensors
from samsara.context_aware.contexts import host as host_contexts
from samsara.context_aware.contexts import vm as vm_contexts
from samsara.context_aware import contexts_repository
from samsara.drivers import virt

LOG = logging.getLogger(__name__)

collector_manager_opts = [
    cfg.IntOpt('host_collect_context_period',
               default=10,
               help='How often (in seconds) to run periodic host contexts collect.'),

    cfg.IntOpt('instances_collect_context_period',
               default=10,
               help='How often (in seconds) to run periodic instances contexts collect.'
               ),
]
CONF = cfg.CONF
CONF.register_opts(collector_manager_opts, 'collector')

virt_driver      = virt.LibvirtDriver()


class CollectorManager(manager.Manager):
    """Samsara Collector Agent."""

    def __init__(self, *args, **kwargs):
        super(CollectorManager, self).__init__(service_name='collector',
                                               *args, **kwargs)

        # Create context repository
        LOG.info('Create context local repository')
        self.ctx_repository = contexts_repository.LocalContextsRepository()

        self.ctx_global_repository = contexts_repository.GlobalContextsRepository()

        #
        # Instantiate Contexts Handlers
        #
        self.host_contexts_handler = host_contexts.HostContexts()

    @periodic_task.periodic_task(spacing=CONF.collector.host_collect_context_period, run_immediately=True)
    def _get_host_context(self,context):
        """ Get Host Contexts and store into repository"""

        # Get host resources usage context
        LOG.info('Get host resources usage context')
        ctx_host_resources_usage = self.host_contexts_handler.get_current_resources_usage()

        # Store into repository
        self.ctx_repository.store_context(ctx_host_resources_usage)
        LOG.info('Store host resources usage context into local repository')

        self.ctx_global_repository.store_context(ctx_host_resources_usage)
        LOG.info('Store host resources usage context into global repository')

        LOG.info('Get Host Contexts and store into repository')


    @periodic_task.periodic_task(spacing=CONF.collector.instances_collect_context_period, run_immediately=True)
    def _get_instances_context(self,context):
        """ Get Virtual Machine Resource Usage Contexts and store into repository"""

        # Get Virtual Machines Contexts and store local repository
        LOG.info('Get Virtual Machines Contexts and store local repository')
        if virt_driver.get_active_instancesID():
            for vm_id in virt_driver.get_active_instancesID():

                # Get vm contexts Handlers
                vm_contexts_handler = vm_contexts.VirtualMachineContexts(vm_id)

                # Get vm resources usage context
                ctx_vm_resources_usage = vm_contexts_handler.get_resources_usage()

                # Store context into repository
                self.ctx_repository.store_context(ctx_vm_resources_usage)

                # Update vcpu_time for all instances
                virt_driver.update_vcpu_time_instances()
                LOG.info('Update VCPU time for all instances')
        else:
            # Reset
            virt_driver.update_vcpu_time_instances(reset=True)
            LOG.info('Reset VCPU time')
