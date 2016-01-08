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
Samsara Local Controller Manager
"""

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_serialization import jsonutils
from oslo_service import periodic_task
from oslo_utils import importutils

#from samsara.common import exception
from samsara.common import manager



LOG = logging.getLogger(__name__)

local_controller_opts = [
    cfg.IntOpt('task_period',
               default=10,
               help='How often (in seconds) to run periodic tasks in '
                    'the scheduler driver of your choice. '
                    'Please note this is likely to interact with the value '
                    'of service_down_time, but exactly how they interact '
                    'will depend on your choice of scheduler driver.'),
]
CONF = cfg.CONF
CONF.register_opts(collector_controller_opts)


class CollectorManager(manager.Manager):
    """Samsara Collector Agent."""

    target = messaging.Target(version='1.0')

    def __init__(self, *args, **kwargs):
        super(CollectorManager, self).__init__(service_name='collector',
                                               *args, **kwargs)


     @periodic_task.periodic_task(spacing=CONF.task_period,
                                  run_immediately=True)
     def _run_periodic_tasks(self, context):
         self.driver.run_periodic_tasks(context)
