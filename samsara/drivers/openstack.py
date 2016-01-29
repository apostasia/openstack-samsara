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

from novaclient import client
from samsara.common import authenticate


class OpenStackDriver(object):

    def __init__(self):
        session = authenticate.get_admin_session()
        self.novaclient = client.Client(2, session=session)

    def listflavors(self):
        flavors = self.novaclient.flavors.list()
        return flavors

    def nova(self):
        return self.novaclient

    def get_all_servers(self):
        servers_list = []
        active_servers = self.novaclient.servers.list(search_opts={'all_tenants':1})

        for server in active_servers:
            active_server                  = {}
            active_server["id"]            = str(server.id)
            active_server["name"]          = str(server.name)
            active_server["instance_name"] = str(server. __getattr__('OS-EXT-SRV-ATTR:instance_name'))
            active_server["host_id"]       = str(server.hostId)
            active_server["host_name"] = str(server. __getattr__('OS-EXT-SRV-ATTR:host'))

            servers_list.append(active_server)
        return servers_list

    def get_servers_by_host(self,host):
        all_servers = self.get_all_servers()
        filtered_servers = [server for server in all_servers if server['host_name'] == host]

        return filtered_servers