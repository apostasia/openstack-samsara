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

""" Credentials Helper """


from oslo_config import cfg

keystone_authtoken_group = cfg.OptGroup('keystone_authtoken')
keystone_authtoken_opts = [ cfg.StrOpt('auth_url', default = 'http://localhost:5000/v3'),
                           cfg.StrOpt('project_domain_id', default = 'default'),
                           cfg.StrOpt('user_domain_id', default = 'default'),
                            cfg.StrOpt('user_domain_name', default = 'default'),
                           cfg.StrOpt('project_domain_name', default = 'default'),
                           cfg.StrOpt('project_name', default = 'admin'),
                           cfg.StrOpt('username', default = 'admin'),
                           cfg.StrOpt('region_name', default = 'RegionOne'),
                           cfg.StrOpt('password', default = 'samsara')]
CONF = cfg.CONF

CONF.register_group(keystone_authtoken_group)
CONF.register_opts(keystone_authtoken_opts, keystone_authtoken_group)

def get_admin_creds():
    creds={}
    creds['auth_url'] = CONF.keystone_authtoken.auth_url
    creds['username'] = CONF.keystone_authtoken.username
    creds['password'] = CONF.keystone_authtoken.password
    creds['project_name'] = CONF.keystone_authtoken.project_name
    creds['user_domain_id'] = CONF.keystone_authtoken.user_domain_id
    creds['user_domain_name'] = CONF.keystone_authtoken.user_domain_name
    creds['project_domain_id'] = CONF.keystone_authtoken.project_domain_id
    creds['project_domain_name'] = CONF.keystone_authtoken.project_domain_name
    return creds
