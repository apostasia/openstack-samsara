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


import libvirt
import untangle

## Hypervisor hosts
hv = [ "tiffy.tuxgeek.de", "ernie.tuxgeek.de" ]

for hv_host in hv:
   uri = "qemu+ssh://virtuser@" + hv_host + "/system"
   conn = libvirt.openReadOnly(uri)

   hypervisor_name = conn.getHostname()

   print "The following machines are running on: " + hypervisor_name

   # List active hosts
   active_hosts = conn.listDomainsID()
   for id in active_hosts:
     dom = conn.lookupByID(id)
     print "System " + dom.name() + " is UP."

   # List inactive Hosts
   for name in conn.listDefinedDomains():
     dom = conn.lookupByName(name)
     print "System " + dom.name() + " is DOWN."
   print
   
def get_default_config_help(self):
    
    
  def _get_host_sysinfo_serial_hardware(self):
        """Get a UUID from the host hardware
        Get a UUID for the host hardware reported by libvirt.
        This is typically from the SMBIOS data, unless it has
        been overridden in /etc/libvirt/libvirtd.conf
        """
        caps = self._host.get_capabilities()
        return caps.host.uuid