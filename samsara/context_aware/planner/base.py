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
        self.cell_contexts_handler = cell.CellContexts()

    def generate_consolidation_plan(self):
        pass

    def generate_load_balance_plan(self, instances):
        pass

    def generate_plan():
        pass
