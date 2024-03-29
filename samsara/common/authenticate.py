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

from keystoneauth1 import loading
from keystoneauth1 import session

from novaclient import client as nova_client

from samsara.common.credentials import *

def get_nova_client():
    creds = get_admin_creds()
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(**creds)
    sess = session.Session(auth=auth)
    nova = nova_client.Client("2", session=sess)
    return nova
