 #!/usr/bin/env python

import libvirt

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