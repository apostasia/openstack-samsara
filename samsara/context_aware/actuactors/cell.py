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

from oslo_log import log as logging

from samsara.context_aware.actuactor import base


LOG = logging.getLogger(__name__)


class CellActuactor(base.BaseActuator):
    def _migrate_to(instance, host):
            pass

    def wake_host(self, host):
            pass

    def sleep_host(self, host):
            pass

    def consolidate(self, consolidation_plan):
            pass

    def balance(self, consolidation_plan):
            pass
