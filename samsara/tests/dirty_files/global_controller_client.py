#!/usr/bin/env python


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

"""Starter script for Samsara Global Controller Client Test."""

import sys
sys.path.append('/home/vagrant/samsara')

from oslo_config import cfg
from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr

from samsara.common import config
from samsara.global_controller import rpcapi as gc_client
#from samsara import utils
from samsara import objects
from samsara import version
#from samsara.common import context as samsara_context
from oslo_context import context 

CONF = cfg.CONF
logging.register_options(CONF)


def main():
    config.parse_args(sys.argv)
    objects.register_all()
    gmr.TextGuruMeditation.setup_autorun(version)
    
    client = gc_client.GlobalManagerAPI()
    ctxt = context.RequestContext()
    response = client.get_host_info(ctxt,host='vagrant-ubuntu-trusty-64')

    print(response)
    print (client.get_host_info_ob(ctxt,host='vagrant-ubuntu-trusty-64'))

if __name__ == "__main__":
    sys.exit(main()) 