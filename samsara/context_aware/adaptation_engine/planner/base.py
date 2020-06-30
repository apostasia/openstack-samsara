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

from oslo_config import cfg
from oslo_log import log as logging

from samsara.context_aware import contexts_repository
from samsara.context_aware.contexts import cell
from samsara.context_aware.adaptation_engine.planner.algorithms import multi_binpacking

LOG = logging.getLogger(__name__)


class Planner(object):

    def __init__(self):

        # Get Allocation Algorithms
        self.allocation_algorithm = multi_binpacking.BestFitDecreased()

    def generate_consolidation_plan(self, active_hosts = [], compute_threshold=0.9, memory_threshold=0.9, *args, **kwargs):

        if not active_hosts:
            return {}

        # Update available resources in according defined thresholds
        active_hosts = self.update_available_resources(active_hosts, compute=compute_threshold, memory=memory_threshold)

        return self.allocation_algorithm.generate_consolidation_plan(active_hosts)

    def generate_load_balance_plan(self, active_hosts = [], inactive_hosts = [], compute_threshold=0.9, memory_threshold=0.9, *args, **kwargs):

        # If not active hosts, return empty plan.
        if active_hosts:
            # Update available resources in according defined thresholds
            active_hosts = self.update_available_resources(active_hosts, compute=compute_threshold, memory=memory_threshold)
        else:
            return {}


        if inactive_hosts:
            # Update available resources in according defined thresholds
            inactive_hosts = self.update_available_resources(inactive_hosts, compute=compute_threshold, memory=memory_threshold)

        return self.allocation_algorithm.generate_load_balance_plan(active_hosts, inactive_hosts)

    def update_available_resources(self, hosts, **thresholds):
        """ Update Available Resources Using defined thresholds """
        updated_hosts = []

        for host in hosts:

            # Calculates maximum compute threshold and maximum memory threshold
            max_compute_threshold = host['compute_capacity'] * thresholds['compute']

            max_memory_threshold = host['memory_capacity'] * thresholds['memory']

            # Calculates available compute and available memory. If available resource is less than zero, return zero.
            host['available_compute'] = max(max_compute_threshold - host['used_compute'], 0)

            host['available_memory'] = max(max_memory_threshold - host['used_memory'], 0)

            # Add host to hosts candidates list
            updated_hosts.append(host)

        return updated_hosts
