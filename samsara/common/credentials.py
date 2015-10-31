
from oslo_config import cfg

keystone_authtoken_group = cfg.OptGroup('keystone_authtoken')
keystone_authtoken_opts = [cfg.StrOpt('auth_uri', default = 'http://localhost:5000'),
                           cfg.StrOpt('auth_url', default = 'http://localhost:35357'),
                           cfg.StrOpt('auth_plugin', default = 'password'),
                           cfg.StrOpt('project_domain_id', default = 'default'),
                           cfg.StrOpt('user_domain_id', default = ' default'),
                           cfg.StrOpt('project_name', default = ' service'),
                           cfg.StrOpt('username', default = 'nova'),
                           cfg.StrOpt('password', default = 'nova')]
CONF = cfg.CONF

CONF.register_group(keystone_authtoken_group)
CONF.register_opts(keystone_authtoken_opts, keystone_authtoken_group)

def get_nova_creds():
    creds={}    
    creds['auth_url'] = CONF.keystone_authtoken.auth_url
    creds['username'] = CONF.keystone_authtoken.username
    creds['password'] = CONF.keystone_authtoken.password
    creds['project_name'] = CONF.keystone_authtoken.project_name
    creds['user_domain_id'] = CONF.keystone_authtoken.user_domain_id
    creds['project_domain_id'] = CONF.keystone_authtoken.project_domain_id
    return creds 