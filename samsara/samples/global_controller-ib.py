# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
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

"""Starter script for Samsara Global Controller."""

import sys
sys.path.append('/home/vagrant/samsara')
import eventlet

from oslo_config import cfg
from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr

from samsara.common import config
from samsara.common import service-ironic-based as samsara_service
#from samsara import utils
from samsara import objects
from samsara import version

CONF = cfg.CONF
CONF.import_opt('samsara_global_controller_topic', 'samsara.global_controller.rpcapi') # import conf from module

logging.register_options(CONF)


def main():
    config.parse_args(sys.argv)
    eventlet.monkey_patch()
    objects.register_all()

    gmr.TextGuruMeditation.setup_autorun(version)

    server = service.Service.create(binary='samsara-global_controller',
                                    topic=CONF.samsara_global_controller_topic)
    
    service.serve(server)
    service.wait()
if __name__ == "__main__":
    sys.exit(main()) 
    
    
import logging
import sys

from oslo_config import cfg
from oslo_service import service



CONF = cfg.CONF


def main():
    # Pase config file and command line options, then start logging
    ironic_service.prepare_service(sys.argv)

    mgr = samsara_service.RPCService(CONF.host,
                                    'samsara.global_controller.manager',
                                    'GlobalControllerManager')

    LOG = logging.getLogger(__name__)
    LOG.debug("Configuration:")
    CONF.log_opt_values(LOG, logging.DEBUG)

    launcher = service.launch(CONF, mgr)
    launcher.wait()


if __name__ == '__main__':
    sys.exit(main())