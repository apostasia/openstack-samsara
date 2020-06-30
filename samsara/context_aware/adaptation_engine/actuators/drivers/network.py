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

""" SSH Host Actuator Driver """

import paramiko
import subprocess
import os
from awake import wol

from oslo_config import cfg
from oslo_log import log as logging


ssh_actuator_driver_opts = [
               cfg.StrOpt('username',
               default="lups",
               help='SSH username to acess host.'),
               cfg.StrOpt('password',
               default="lups999",
               help='SSH user password .'),
]
CONF = cfg.CONF
CONF.register_opts(ssh_actuator_driver_opts, group= 'ssh_driver')

LOG = logging.getLogger(__name__)

class SSHDriver(object):
    def __init__(self):
        self.username   = CONF.ssh_driver.username
        self.password   = CONF.ssh_driver.password
    def run_cmd(self, host, command):
        """Execute this command on host"""

        cmd = 'sudo samsara-rootwrap /etc/samsara/rootwrap.conf %s' % command
        try:
            ssh_client =  paramiko.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())

            ssh_client.connect(host, username=self.username, password=self.password)

            # Send the command
            stdin, stdout, stderr = ssh_client.exec_command(cmd)

            LOG.info("Run command %s on %s host", command, host)
            return True

        except paramiko.SSHException:
            LOG.error("Not run comand %s on %s host", command, host)
            return False

        finally:
            # Close Connection
            ssh_client.close()


class NetworkDriver(object):

    @staticmethod
    def host_is_alive(hostname):

        return_code = subprocess.call(['ping', '-c', '5', '-W', '3', hostname],
                                   stdout=open(os.devnull, 'w'),
                                   stderr=open(os.devnull, 'w'))
        if return_code == 0:
            return True
        else:
            return False

    @staticmethod
    def wake_on_lan(macaddress):

        LOG.info('Wake node with physical address %s by WOL', macaddress)
        wol.send_magic_packet(macaddress)
