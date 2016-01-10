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
from samsara.context_aware import contexts
from samsara.context_aware import contexts_repository
from samsara.drivers import virt

LOG = logging.getLogger(__name__)

collector_manager_opts = [
    cfg.IntOpt('task_period',
               default=10,
               help='How often (in seconds) to run periodic tasks in '
                    'the scheduler driver of your choice. '
                    'Please note this is likely to interact with the value '
                    'of service_down_time, but exactly how they interact '
                    'will depend on your choice of scheduler driver.'),
]
CONF = cfg.CONF
CONF.register_opts(collector_manager_opts)

virt_driver      = virt.LibvirtDriver()


class CollectorManager(manager.Manager):
    """Samsara Collector Agent."""

    def __init__(self, *args, **kwargs):
        super(CollectorManager, self).__init__(service_name='collector',
                                               *args, **kwargs)

        # Create context repository
        LOG.info('Create context repository')
        self.ctx_repository = contexts_repository.LocalContextsRepository()

    @periodic_task.periodic_task(spacing=CONF.task_period, run_immediately=True)
    def _get_host_context(self,context):
        """ Get Host Contexts and store into repository"""

        # Get host resources usage context
        ctx_host_resources_usage = contexts.HostResourceUtilization('host_resources_usage').getContext()

        LOG.debug(ctx_host_resources_usage)

        # Store into repository
        self.ctx_repository.store_context(ctx_host_resources_usage)

        LOG.info(self.ctx_repository.list_context_vars('host_resources_usage'))

        # notifier.info({'some': 'context'}, 'host.get_resources', 'ok')

        LOG.info('Get Host Contexts and store into repository')


    @periodic_task.periodic_task(spacing=CONF.task_period, run_immediately=True)
    def _get_instances_context(self,context):
        """ Get Virtual Machine Resource Usage Contexts and store into repository"""

        # Get Virtual Machine Contexts
        for vm_id in virt_driver.get_active_instacesID():

            # Get instance (vm) resources usage context
            ctx_vm_resources_usage = contexts.VirtualMachineResourceUtilization('vm_resources_usage',vm_id).getContext()

            # Store into repository
            self.ctx_repository.store_context(ctx_vm_resources_usage)

        LOG.info('Collect Contexts: OK')

        # Update vcpu_time for all instances
        virt_driver.update_vcpu_time_instances()
        LOG.info('Update VCPU time for all instances')
