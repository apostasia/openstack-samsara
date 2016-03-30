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


class HostContexts(base.BaseContext):
    """ Class Representing Hosts Contexts"""
    def __init__(self):

        # Start Local Repository
        self.ctx_repository = ctx_repository.LocalContextsRepository()

    def get_host_info(self):

        tag = "host_info"
        context = collections.namedtuple(tag,
        ['hostname',
        'uuid',
        'cpu_number',
        'compute_capacity',
        'memory_capacity',
        'mgmt_nic_speed',
        'mgmt_nic_hwaddr',
        'created_at'])

        hostname        = host_sensors.HostNetworkHostnameSensor.read_value()
        uuid            = host_sensors.HostIdSensor.read_value()
        cpu_number      = host_sensors.HostCPUNumberSensor.read_value()
        max_compute     = host_sensors.HostComputeCapacitySensor.read_value()
        max_memory      = host_sensors.HostMemoryCapacitySensor.read_value()
        mgmt_nic_speed  = host_sensors.HostNetworkNicCapacitySensor.read_value()
        mgmt_nic_hwaddr = host_sensors.HostNetworkNicHwAddressSensor.read_value()

        created_at          = datetime.utcnow().isoformat()

        return context(hostname,
                            uuid,
                            cpu_number,
                            max_compute,
                            max_memory,
                            mgmt_nic_speed,
                            mgmt_nic_hwaddr,
                            created_at)



    def get_avg_resources_usage(self, time_frame, method=None):

        tag = "host_avg_resources_usage"
        context = collections.namedtuple(tag,
        ['hostname',
        'uuid',
        'avg_compute_usage',
        'avg_compute_avail',
        'avg_memory_usage',
        'avg_memory_avail',
        'created_at'])

        created_at     = datetime.utcnow().isoformat()

        # Historical Compute Usage per periodo defined in time frame
        historical_compute_usage = self.get_compute_usage_last_period(time_frame)
        LOG.info('Samples in MIPS: %s', historical_compute_usage)

        # Historical Compute Usage per periodo defined in time frame
        historical_memory_usage = self.get_memory_usage_last_period(time_frame)
        LOG.info('Samples in MBytes: %s', historical_memory_usage)

        # Get basic host information
        hostname          = self.get_host_info().hostname
        uuid              = self.get_host_info().uuid
        compute_capacity  = self.get_host_info().compute_capacity
        memory_capacity   = self.get_host_info().memory_capacity

        # Calculate average compute usage and compute available
        avg_compute_usage = np.average(historical_compute_usage)
        avg_compute_avail = compute_capacity - avg_compute_usage

        # Calculate average memory usage and memory available - TODO: mover para um método especializado
        avg_memory_usage = np.average(historical_memory_usage)
        avg_memory_avail = memory_capacity - avg_memory_usage

        created_at          = datetime.utcnow().isoformat()


        return context(hostname,
                            uuid,
                            avg_compute_usage,
                            avg_compute_avail,
                            avg_memory_usage,
                            avg_memory_avail,
                            created_at)

    def get_resources_usage(self, time_frame, method=None):

        tag = "host_avg_resources_usage"
        context = collections.namedtuple(tag,
        ['hostname',
        'uuid',
        'used_compute',
        'available_compute',
        'used_memory',
        'available_memory',
        'created_at'])

        created_at     = datetime.utcnow().isoformat()

        # Historical Compute Usage per periodo defined in time frame
        historical_compute_usage = self.get_compute_usage_last_period(time_frame)
        LOG.info('Samples in MIPS: %s', historical_compute_usage)

        # Historical Compute Usage per periodo defined in time frame
        historical_memory_usage = self.get_memory_usage_last_period(time_frame)
        LOG.info('Samples in MBytes: %s', historical_memory_usage)

        # Get basic host information
        hostname          = self.get_host_info().hostname
        uuid              = self.get_host_info().uuid
        compute_capacity  = self.get_host_info().compute_capacity
        memory_capacity   = self.get_host_info().memory_capacity

        # Calculate average compute usage and compute available
        used_compute = np.average(historical_compute_usage)
        available_compute = compute_capacity - used_compute

        # Calculate average memory usage and memory available - TODO: mover para um método especializado
        used_memory     = np.average(historical_memory_usage)
        available_memory = memory_capacity - used_memory

        created_at          = datetime.utcnow().isoformat()


        return context(hostname,
                            uuid,
                            used_compute,
                            available_compute,
                            used_memory,
                            available_memory,
                            created_at)




    def get_current_resources_usage(self):

        tag = "host_resources_usage"
        context = collections.namedtuple(tag, ['compute_utilization',
        'memory_utilization',
        'created_at'])

        compute_utilization = host_sensors.HostComputeUsageSensor.read_value()
        memory_utilization  = host_sensors.HostMemoryUsageSensor.read_value()
        created_at          = datetime.utcnow().isoformat()

        return context(compute_utilization,
                            memory_utilization,
                            created_at)

    def get_historical_compute_usage(self, limit=10):
        """ Get historical data about host compute usage from local context repository
        """

        historical_data = [ctx['compute_utilization'] for ctx in  self.ctx_repository.retrieve_last_n_contexts('host_resources_usage', limit)]

        return historical_data

    def get_historical_memory_usage(self, limit=10):
        """ Get historical data about host memory usage from local context repository
        """

        historical_data = [ctx['memory_utilization'] for ctx in  self.ctx_repository.retrieve_last_n_contexts('host_resources_usage', limit)]

        return historical_data

    def get_compute_usage_last_period(self, period):
        """ Get stored data about host compute usage from local context repository
        """
        stored_data = [ctx['compute_utilization'] for ctx in  self.ctx_repository.retrieve_last_contexts_from_period('host_resources_usage', period)]

        return stored_data

    def get_memory_usage_last_period(self, period):
        """ Get stored data about host memory usage from local context repository
        """
        stored_data = [ctx['memory_utilization'] for ctx in  self.ctx_repository.retrieve_last_contexts_from_period('host_resources_usage', period)]

        return stored_data

    def get_active_instances(self):
        """ Return the active virtual machines in the host."""

        context = collections.namedtuple('active_instances', ['instances','created_at'])

        active_instances = []

        for instance_uuid in hypervisor_sensors.ActiveVirtualMachinesSensor.read_value():
            active_instances.append(self.ctx_repository.get_last_context(tag='vm_resources_usage', uuid=instance_uuid))


        created_at = datetime.utcnow().isoformat()

        return context(active_instances, created_at)
