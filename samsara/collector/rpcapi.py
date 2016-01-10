"""
Client side of the samsara collector RPC API.
"""

from oslo_config import cfg

import oslo_messaging as messaging

from samsara.common import context as samsara_context
from samsara.objects import base as objects_base
from samsara.common import rpc

rpcapi_opts = [
    cfg.StrOpt('samsara_collector_topic',
               default='samsara_collector',
               help='The topic samsara collector nodes listen on'),
]

CONF = cfg.CONF
CONF.register_opts(rpcapi_opts)

rpcapi_cap_opt = cfg.StrOpt('samsara_collector',
        help='Set a version cap for messages sent to samsara collector services')
CONF.register_opt(rpcapi_cap_opt, 'upgrade_levels')


class CollectorManagerAPI(object):
    '''Client side of the samsara collector manager rpc API.

    API version history:

        * 1.0 - Initial version.
    '''

    VERSION_ALIASES = {
        'kilo': '1.0',
    }

    def __init__(self):
        super(CollectorManagerAPI, self).__init__()
        target = messaging.Target(topic=CONF.samsara_collector_topic, version='1.0')
        version_cap = self.VERSION_ALIASES.get(CONF.upgrade_levels.samsara_collector,
                                               CONF.upgrade_levels.samsara_collector)

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
