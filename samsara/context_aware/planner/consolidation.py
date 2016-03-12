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

from samsara.context_aware.contexts import cell

LOG = logging.getLogger(__name__)


class Planner(object):

    def __init__(self):
        self.ctx_cell = cell.CellContexts()

    def generate_consolidation_plan(self, instances):

        active_hosts = ctx_cell.get_active_hosts()
        ctx_cell.get_underloaded_hosts()
        ctx_cell.get_inactive_hosts()


OrderedDict(sorted(cell_ctx[0].items, key=lamba t:[0]))
OrderedDict(sorted(cell_ctx[0].items, key=lamba t: t[0]))
OrderedDict(sorted(cell_ctx[0].items, key=lambda t: t[0]))
OrderedDict(sorted(cell_ctx[0].items(), key=lambda t: t[0]))
OrderedDict(sorted(cell_ctx[0].items(), key=lambda t: t[0]))
hosts = cell_ctx[0]
hosts
sorted(hosts. key=lamba k: k['available_compute'])
sorted(hosts. key=lambda k: k['available_compute'])
sorted(hosts, key=lambda k: k['available_compute'])
sorted(hosts, key=lambda k: k['available_compute'], reverse=True)
sorted(hosts, key=lambda k: k['available_compute'], reverse=True)
sorted(hosts, key=lambda k: k['available_compute'])
[ host[0]  for host in sorted(hosts, key=lambda k: k['available_compute'])




]
[ host[0]  for host in sorted(hosts, key=lambda k: k['available_compute'])]
[ host[0] for host in sorted(hosts, key=lambda k: k['available_compute'])]
sorted(hosts, key=lambda k: k['available_compute'])
for host in sorted(hosts, key=lambda k: k['available_compute']):
    print host[0][0]
sorted(hosts, key=lambda k: k['available_compute'])
host_sorted = sorted(hosts, key=lambda k: k['available_compute'])
host_sorted[0]
host_sorted[0][0]
host_sorted[0]['hostname']
for host in sorted(hosts, key=lambda k: k['available_compute']):
    print host[0]['hostname']
for host in sorted(hosts, key=lambda k: k['available_compute']):
    print host
for host in sorted(hosts, key=lambda k: k['available_compute']):
    print host[0]
for host in sorted(hosts, key=lambda k: k['available_compute']):
    print host['hostname']
for host in sorted(hosts, key=lambda k: k['available_compute']):
    print host['hostname']


def generate_plan():

    con
