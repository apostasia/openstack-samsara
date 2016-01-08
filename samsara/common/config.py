# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# Copyright 2012 Red Hat, Inc.
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

from oslo_config import cfg
from oslo_db import options
from oslo_log import log

#from samsara.db.sqlalchemy import api as sqlalchemy_api
#from samsara.common import debugger
from samsara.common import paths
from samsara.common import rpc
from samsara import version


CONF = cfg.CONF

_DEFAULT_SQL_CONNECTION = 'sqlite:///' + paths.state_path_def('samsara.sqlite')

_DEFAULT_LOG_LEVELS = ['amqp=WARN', 'amqplib=WARN', 'boto=WARN',
                       'qpid=WARN', 'sqlalchemy=WARN',
                       'oslo_messaging=INFO', 'iso8601=WARN',
                       'urllib3.connectionpool=WARN', 'websocket=WARN',
                       'keystonemiddleware=WARN', 'routes.middleware=WARN',
                       'stevedore=WARN']

_DEFAULT_LOGGING_CONTEXT_FORMAT = ('%(asctime)s.%(msecs)03d %(process)d '
                                   '%(levelname)s %(name)s [%(request_id)s '
                                   '%(user_identity)s] %(instance)s'
                                   '%(message)s')


def parse_args(argv, default_config_files=None, configure_db=False):
    log.set_defaults(_DEFAULT_LOGGING_CONTEXT_FORMAT, _DEFAULT_LOG_LEVELS)
    log.register_options(CONF)

    CONF.set_override('log_file', '/var/log/samsara/samsara-global.log')
    CONF.set_override('debug', 'True')
    log.setup(CONF, 'samsara-global_controller')


    options.set_defaults(CONF, connection=_DEFAULT_SQL_CONNECTION,
                         sqlite_db='samsara.sqlite')
    rpc.set_defaults(control_exchange='samsara')
    #debugger.register_cli_opts()
    CONF(argv[1:],
         project='samsara',
         version=version.version_string(),
         default_config_files=default_config_files)
    rpc.init(CONF)

    if configure_db:
        sqlalchemy_api.configure(CONF)
