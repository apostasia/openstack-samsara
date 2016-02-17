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

from oslo_config import cfg
from oslo_log import log as logging


from samsara.context_aware.actuactor import base


LOG = logging.getLogger(__name__)

host_actuactor_opts = [ cfg.StrOpt('rootwrap_config', default = "/etc/samsara/rootwrap.conf", help = 'Path to the rootwrap configuration file to use'
'running commands as root.')
]

CONF = cfg.CONF
CONF.register_opt(host_actuactor_opts) 


class HostActuactor(base.BaseActuator):

    def _get_root_helper(self):
        return 'sudo samsara-rootwrap %s' % CONF.rootwrap_config

    def execute(self):
        pass
