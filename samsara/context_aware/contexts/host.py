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


import abc
import collections
from datetime import datetime
import numpy as np
import time
from oslo_log import log as logging

from samsara.context_aware import base
from samsara.context_aware.sensors import host as host_sensors
from samsara.context_aware.sensors import hypervisor as hypervisor_sensors
from samsara.context_aware import contexts_repository as ctx_repository

LOG = logging.getLogger(__name__)


class HostInfo(base.BaseContext):

    def __init__(self):
        self.tag = "host_info"
        self.context = collections.namedtuple(self.tag,
        ['hostname',
        'uuid',
        'cpu_number',
        'compute_capacity',
        'memory_capacity',
        'mgmt_nic_speed',
        'mgmt_nic_hwaddr',
        'created_at'])

    def getContext(self):

        hostname        = host_sensors.HostNetworkHostnameSensor.read_value()
        uuid            = host_sensors.HostIdSensor.read_value()
        cpu_number      = host_sensors.HostCPUNumberSensor.read_value()
        max_compute     = host_sensors.HostComputeCapacitySensor.read_value()
        max_memory      = host_sensors.HostMemoryCapacitySensor.read_value()
        mgmt_nic_speed  = host_sensors.HostNetworkNicCapacitySensor.read_value()
        mgmt_nic_hwaddr = host_sensors.HostNetworkNicHwAddressSensor.read_value()

        created_at          = datetime.utcnow().isoformat()

        return self.context(hostname,
                            uuid,
                            cpu_number,
                            max_compute,
                            max_memory,
                            mgmt_nic_speed,
                            mgmt_nic_hwaddr,
                            created_at)



class HostAvgResourcesUsage(base.BaseContext):
    def __init__(self):

        self.tag = "host_avg_resources_usage"
        self.context = collections.namedtuple(self.tag,
        ['hostname',
        'uuid',
        'compute_usage_avg',
        'memory_usage_avg',
        'created_at'])

        created_at     = datetime.utcnow().isoformat()

        # Instantiate Stored Host Compute Contexts Handlers
        self.stored_ctx_host = StoredHostComputeUsage()

    def get_context(self, time_frame, method=None):

        # Historical Compute Usage per periodo defined in time frame
        historical_compute_usage = self.stored_ctx_host.get_last_period_contexts(time_frame)
        LOG.info('Samples in MIPS: %s', historical_compute_usage)

        # Get basic host information
        hostname          = host_sensors.HostNetworkHostnameSensor.read_value()
        uuid              = host_sensors.HostIdSensor.read_value()

        # Calculate average compute usage
        compute_usage_avg = np.average(historical_compute_usage)

        # Calculate average memory usage - TODO: to implement
        memory_usage_avg  = 0

        created_at          = datetime.utcnow().isoformat()


        return self.context(hostname,
                            uuid,
                            compute_usage_avg,
                            memory_usage_avg,
                            created_at)


class HostResourcesUsage(base.BaseContext):

    def __init__(self):
        self.tag = "host_resources_usage"
        self.context = collections.namedtuple(self.tag, ['compute_utilization',
        'memory_utilization',
        'created_at'])

    def getContext(self):

        compute_utilization = host_sensors.HostComputeUsageSensor.read_value()
        memory_utilization  = host_sensors.HostMemoryUsageSensor.read_value()
        created_at          = datetime.utcnow().isoformat()

        return self.context(compute_utilization,
                            memory_utilization,
                            created_at)


class HistoricalHostComputeUsage(base.BaseContext):
    """ Host Compute Usage Historical Context """

    def __init__(self, context_tag):
        self.ctx_repository = ctx_repository.LocalContextsRepository()

    def getContext(self, limit=10):
        """ Get historical data about host compute usage from local context repository
        """

        historical_data = [ctx['compute_utilization'] for ctx in  self.ctx_repository.retrieve_last_n_contexts('host_resources_usage', limit)]

        return historical_data

class StoredHostComputeUsage(base.BaseContext):
    """ Store Host Compute Usage Context """

    def __init__(self):
        context_tag = "store_host_compute_usage"
        self.ctx_repository = ctx_repository.LocalContextsRepository()

    def getContext(self, limit=10):
        """ Get stored data about host compute usage from local context repository
        """
        stored_data = [ctx['compute_utilization'] for ctx in  self.ctx_repository.retrieve_last_n_contexts('host_resources_usage', limit)]

        return stored_data

    def get_last_period_contexts(self, period):
        """ Get stored data about host compute usage from local context repository
        """
        stored_data = [ctx['compute_utilization'] for ctx in  self.ctx_repository.retrieve_last_contexts_from_period('host_resources_usage', period)]

        return stored_data

class ActiveVirtualMachines(base.BaseContext):
    """ Representing the active virtual machines in the host."""

    def __init__(self, context_tag):
        self.context = collections.namedtuple(context_tag, ['active_vms','created_at'])


    def getContext(self):

        active_vms = hypervisor_sensors.ActiveVirtualMachinesSensor.read_value()
        created_at = datetime.utcnow().isoformat()

        return self.context(active_vms, created_at)
