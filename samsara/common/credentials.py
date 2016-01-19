
from oslo_config import cfg

keystone_authtoken_group = cfg.OptGroup('keystone_authtoken')
keystone_authtoken_opts = [ cfg.StrOpt('auth_url', default = 'http://localhost:5000/v3'),
                           cfg.StrOpt('project_domain_id', default = 'Default'),
                           cfg.StrOpt('user_domain_id', default = 'Default'),
                            cfg.StrOpt('user_domain_name', default = 'Default'),
                           cfg.StrOpt('project_domain_name', default = 'Default'),
                           cfg.StrOpt('project_name', default = 'admin'),
                           cfg.StrOpt('username', default = 'admin'),
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
