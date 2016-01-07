# Example-35.py
from __future__ import print_function
import sys
import libvirt
from datetime import datetime


conn = libvirt.open('qemu:///system')
domains=  conn.listAllDomains()
domain_dict={}
for domain in domains:   
    libvirt_status = domain.state()
    if libvirt_status[0] == libvirt.VIR_DOMAIN_RUNNING or libvirt_status[0] == libvirt.VIR_DOMAIN_SHUTDOWN:
    
        uuid = domain.UUIDString()                 # Get UUID id
        max_memory_alocated = domain.maxMemory()   # Get maximum alocated memory to domain     
        aggregate_vcpu_utilization = domain.info()[3]*domain.info()[4] # nr_vcpu * vcpu_time
        print ("VM Id "+str(uuid)+" CPU Use (Ns): "+str(aggregate_vcpu_utilization)+" Mem Use (%): "+str(max_memory_alocated)+" "+datetime.utcnow().isoformat())
conn.close