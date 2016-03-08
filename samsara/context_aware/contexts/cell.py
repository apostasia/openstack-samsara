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

from __future__ import print_function
import collections
from datetime import datetime
import numpy as np
import time
from oslo_config import cfg
from oslo_log import log as logging

from samsara.context_aware import base
from samsara.context_aware.sensors import host as host_sensors
from samsara.context_aware.sensors import hypervisor as hypervisor_sensors
from samsara.context_aware import contexts_repository

LOG = logging.getLogger(__name__)


class CellContexts(base.BaseContext):
    """ Representing  the cloud cell contexts."""

    def __init__(self):

        # Global Repository
        self.ctx_global_repository = contexts_repository.GlobalContextsRepository()

    def get_active_hosts(self):
        """ Return active host in the cloud cell"""

        context = collections.namedtuple('active_hosts', ['hosts','created_at'])

        repository_handler = self.ctx_global_repository.get_repository_handler()


        hosts = [ dict(host) for host in repository_handler['host_situation'].find(situation=['normal', 'underload', 'overload'])]

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_inactive_hosts(self):
        """ Return inactive hosts in the cloud cell"""

        context = collections.namedtuple('inactive_hosts', ['hosts','created_at'])

        repository_handler = self.ctx_global_repository.get_repository_handler()


        hosts = [ dict(host) for host in repository_handler['host_situation'].find(situation=['sleep', 'hibernate', 'off'])]

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_inactive_hosts(self):
        """ Return inactive hosts in the cloud cell"""

        context = collections.namedtuple('inactive_hosts', ['hosts','created_at'])

        repository_handler = self.ctx_global_repository.get_repository_handler()


        hosts = [ dict(host) for host in repository_handler['host_situation'].find(situation=['sleep', 'hibernate', 'off'])]

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_tasks_status(self):
        pass
