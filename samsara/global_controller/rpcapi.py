# Copyright 2013, Red Hat, Inc.
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
Client side of the samsara global manager RPC API.
"""

from oslo_config import cfg

import oslo_messaging as messaging

from samsara.common import context as samsara_context
from samsara.objects import base as objects_base
from samsara.common import rpc

rpcapi_opts = [
    cfg.StrOpt('samsara_global_controller_topic',
               default='samsara_global_controller',
               help='The topic samsara global nodes listen on'),
]

CONF = cfg.CONF
CONF.register_opts(rpcapi_opts)

rpcapi_cap_opt = cfg.StrOpt('samsara_global',
        help='Set a version cap for messages sent to samsara global services')
CONF.register_opt(rpcapi_cap_opt, 'upgrade_levels')


class GlobalControllerAPI(object):
    '''Client side of the samsara global controller manager rpc API.

    API version history:

        * 1.0 - Initial version.
    '''

    VERSION_ALIASES = {
        'kilo': '1.0',
    }

    def __init__(self):
        super(GlobalControllerAPI, self).__init__()
        target = messaging.Target(topic=CONF.samsara_global_controller_topic, version='1.0')
        version_cap = self.VERSION_ALIASES.get(CONF.upgrade_levels.samsara_global,
                                               CONF.upgrade_levels.samsara_global)

        serializer = objects_base.SamsaraObjectSerializer()
        self.client = rpc.get_client(target, version_cap=version_cap,
                                     serializer=serializer)


    def get_host_info(self,ctx,host):
        ''' Get info from specific host

        '''
        version = '1.0'
        cctxt = self.client.prepare(server=host, version=version)
        return cctxt.call(ctx,'get_host_info')

    def get_host_info_ob(self,ctx,host):
        ''' Get info from specific host

        '''
        version = '1.0'
        cctxt = self.client.prepare(server=host, version=version)
        return cctxt.call(ctx,'get_host_info_ob')

    def update_host_workload_state(self, context, host, state):
        ''' Get info from specific host

        '''
        version = '1.0'
        cctxt = self.client.prepare(server="controller", version=version)
        cctxt.call(context,'update_host_workload_state', host=host, state=state)
