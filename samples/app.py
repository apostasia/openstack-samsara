from __future__ import print_function
from oslo_config import cfg
 
 
opt_simple_group = cfg.OptGroup(name='simple',
                         title='A Simple Example')
 
opt_morestuff_group = cfg.OptGroup(name='morestuff',
                         title='A More Complex Example')
 
simple_opts = [
    cfg.BoolOpt('enable', default=False,
                help=('True enables, False disables'))
]
 
morestuff_opts = [
    cfg.StrOpt('message', default='No data',
               help=('A message')),
    cfg.ListOpt('usernames', default=None,
                help=('A list of usernames')),
    cfg.DictOpt('jobtitles', default=None,
                help=('A dictionary of usernames and job titles')),
    cfg.IntOpt('payday', default=30,
                help=('Default payday monthly date')),
    cfg.FloatOpt('pi', default=0.0,
                help=('The value of Pi'))
]
 
CONF = cfg.CONF
 
CONF.register_group(opt_simple_group)
CONF.register_opts(simple_opts, opt_simple_group)
 
CONF.register_group(opt_morestuff_group)
CONF.register_opts(morestuff_opts, opt_morestuff_group)
 
 
if __name__ == "__main__":
    CONF(default_config_files=['samsara.conf'])
    print('(simple) enable: {}'.format(CONF.simple.enable))
    print('(morestuff) message :{}'.format(CONF.morestuff.message))
    print('(morestuff) usernames: {}'.format(CONF.morestuff.usernames))
    print('(morestuff) jobtitles: {}'.format(CONF.morestuff.jobtitles))
    print('(morestuff) payday: {}'.format(CONF.morestuff.payday))
    print('(morestuff) pi: {}'.format(CONF.morestuff.pi))