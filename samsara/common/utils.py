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

from cpuinfo import cpuinfo
from operator import sub
import time
import psutil
import libvirt
import os,sys
import re
from lxml import etree,objectify

# This is a backport of the subprocess standard library module from Python 3.2 &
# 3.3 for use on Python 2. It includes bugfixes and some new features. On POSIX
# systems it is guaranteed to be reliable when used in threaded applications. It
# includes timeout support from Python 3.3 but otherwise matches 3.2’s API. It has
#  not been tested on Windows

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess
    

def get_max_mips_percore():
    """Return the max mips percore
    """
    mips_percore = []
    with open("/proc/cpuinfo") as f:
        for line in f:
            if not line.startswith("bogomips"):
                continue
            parts = line.split()
            mips_percore.append(float(parts[2]))
      
    return mips_percore
    
def get_max_mips():  
    return sum(get_max_mips_percore())

def get_max_freq_percore():
    """Get máx frequency CPU per core
       Return an int value in MHz 
    """
    max_freq_percore = []
    
    cpus = [cpu for cpu in os.listdir("/sys/devices/system/cpu") if re.match(r'\b(cpu)(\d+)\b',cpu)]
    for cpu in cpus:
        cmd = ["cat","/sys/devices/system/cpu/%s/cpufreq/cpuinfo_max_freq" % (cpu)]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        max_freq_percore.append(float(process.stdout.read().strip("\n"))/1000) # In MHz
    return max_freq_percore
    
def get_current_freq_percore():
    """Get current frequency CPU per core
       Return an int value in MHz 
    """
    current_freq_percore = []
    cpus = [cpu for cpu in os.listdir("/sys/devices/system/cpu") if re.match(r'\b(cpu)(\d+)\b',cpu)]
    for cpu in cpus:
        cmd = ["cat","/sys/devices/system/cpu/%s/cpufreq/scaling_cur_freq" % (cpu)]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        current_freq_percore.append(float(process.stdout.read().strip("\n"))/1000) # In MHz
    return current_freq_percore
    
# def get_current_freq_percore():
#     freq_percore = []
#     with open("/proc/cpuinfo") as f:
#         for line in f:
#             if not line.startswith("cpu MHz"):
#                 continue
#             parts = line.split()
#             freq_percore.append(float(parts[3]))
#
#     return freq_percore
     
def get_busytime_percore(interval=1):
    
    cpu_time_t0  = [float(t[0])+float(t[2]) for t in psutil.cpu_times(percpu=True)]
    time.sleep(interval)
    cpu_time_t1  = [float(t[0])+float(t[2]) for t in psutil.cpu_times(percpu=True)]
    
    # compute the delta time for each cpu and generate an list
    busytime_percore = map(sub,cpu_time_t1,cpu_time_t0)
    
    return busytime_percore
    
    
def get_usage_mips_percore():
     maxmips_percore               = get_max_mips_percore()
     maxfreq_percore               = get_max_freq_percore()
     currentfreq_percore           = get_current_freq_percore()
     utilized_cputime_percore      = get_busytime_percore()
     
     usage_percore = []
     
     for maxmips,maxfreq,currentfreq,utilized_cputime in zip(maxmips_percore,maxfreq_percore,currentfreq_percore,utilized_cputime_percore):
         usage_percore.append(int((((currentfreq * maxmips)/maxfreq) * utilized_cputime)))
         
     return usage_percore

def get_usage_perc_percore():
     maxmips_percore    = get_max_mips_percore()
     usage_mips_percore = get_usage_mips_percore()
     
     usage_percore = []
     
     for maxmips,usage_mips in zip(maxmips_percore,usage_mips_percore):
         usage_percore.append(round((usage_mips * 100)/maxmips))
         
     return usage_percore

def get_vms():  
    conn = libvirt.openReadOnly('')
    if conn is None:
        print 'Failed to open connection to the hypervisor'
    sys.exit(1)

    for domain_id in conn.listDomainsID():
        domain_instance = conn.lookupByID(domain_id)
        name = domain_instance.name()

def get_host_nic_speed(nic):
    """ Get current speed for informed NIC 
        Return an int value in Mbits per second (Mb/s)
    """
    try:
        file_path = "/sys/class/net/%s/speed"  % (nic)
        nic_speed = open(file_path,"r").read().strip("\n")
        return int(nic_speed)
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)

def get_host_uuid():
    """Get a UUID from the host hardware
    Get a UUID for the host hardware reported by libvirt.
    This is typically from the SMBIOS data, unless it has
    been overridden in /etc/libvirt/libvirtd.conf
    """
    capabilities = objectify.fromstring(conn.getCapabilities())
    return capabilities.host.uuid

def get_vbusytime_percore(libvirt_domain_id,interval=1):
    """ Return the busy time per core/cpu (in seconds) for an VM in the interval
    """
    
    #Get the cpu time intervals 
    vcpu_time_t0  = [float(phys_cpu['cpu_time']) for phys_cpu in dom.getCPUStats(False,0)]
    time.sleep(interval)
    vcpu_time_t1  = [float(phys_cpu['cpu_time']) for phys_cpu in dom.getCPUStats(False,0)]
    
    # compute the delta time for each cpu, convert to seconds and generate an list 
    vbusytime_percore = [float(diff_time)/1000000000 for diff_time in map(sub,vcpu_time_t1,vcpu_time_t0)]
    
    return vbusytime_percore

def get_vm_usage_mips_percore(id=5,interval=1):
     """ Return the usage mips per core/cpu for  an VM in the interval
     """ 
     
     host_compute_capacity_percore = get_max_mips_percore()
     host_maxfreq_percore          = get_max_freq_percore()
     host_currentfreq_percore      = get_current_freq_percore()
     vm_utilized_cputime_percore  = get_vbusytime_percore(id,interval)
     
     usage_percore = []
     
     for compute_capacity,maxfreq,currentfreq,vm_utilized_cputime in zip(host_compute_capacity_percore,host_maxfreq_percore,host_currentfreq_percore,vm_utilized_cputime_percore):
         usage_percore.append(int((((currentfreq * compute_capacity)/maxfreq) * vm_utilized_cputime)))
         
     return usage_percore
     
def get_vm_usage_perc():
     host_compute_capacity_percore = get_max_mips_percore()
     vm_usage_mips_percore         = get_vm_usage_mips_percore()
     
     usage_percore = []
     
     for host_compute_capacity,vm_usage_mips in zip(host_compute_capacity_percore,vm_usage_mips_percore):
         usage_percore.append((float(vm_usage_mips) * 100)/host_compute_capacity)
         
     return sum(usage_percore)
     
def get_vm_alloc_memory():
        dom.maxMemory()
        

    
    
     