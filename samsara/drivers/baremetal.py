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

import glob
import multiprocessing
import os
import re
import socket
import sys
import time
from operator import sub

from lxml import etree, objectify

import psutil
from oslo_log import log as logging

# This is a backport of the subprocess standard library module from Python 3.2 &
# 3.3 for use on Python 2. It includes bugfixes and some new features. On POSIX
# systems it is guaranteed to be reliable when used in threaded applications. It
# includes timeout support from Python 3.3 but otherwise matches 3.2’s API. It has
#  not been tested on Windows

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

cpu_time_percore =  [float(t[0])+float(t[2]) for t in psutil.cpu_times(percpu=True)]

class BareMetalDriver(object):
    def __init__(self):
        pass


    def get_number_cpu(self):
        return multiprocessing.cpu_count()


    def get_max_mips_percore(self):
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

    def get_max_mips(self):
        """Get max MIPS
           Return an int value in MIPS
        """
        return sum(self.get_max_mips_percore())


    def get_max_freq_percore(self):
        """Get max frequency CPU per core
           Return an int value in MHz
        """
        if glob.glob("/sys/devices/system/cpu/**/cpufreq"):
            return self.get_max_freq_percore_by_cpufreq()
        else:
            return self.get_max_freq_percore_by_cpuinfo()

    def get_max_freq_percore_by_cpufreq(self):
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

    def get_max_freq_percore_by_cpuinfo(self):
        """Get max frequency CPU per core by cpuinfo file
           Return an int value in MHz
        """
        max_freq_percore = []
        with open("/proc/cpuinfo") as f:
            for line in f:
                if not line.startswith("model name"):
                    continue
                max_freq = float(re.match(r'model name\s+:\s+.*@\s(\d+\.*\d*)GHz|MHz',line).group(1))*1000
                max_freq_percore.append(max_freq)
        return max_freq_percore

    def get_current_freq_percore(self):
        """Get current frequency CPU per core
           Return an int value in MHz
        """
        if glob.glob("/sys/devices/system/cpu/**/cpufreq"):
            return self.get_current_freq_percore_by_cpufreq()
        else:
            return self.get_current_freq_percore_by_cpuinfo()


    def get_current_freq_percore_by_cpufreq(self):
        """Get current frequency CPU per core by cpufreq file
           Return an int value in MHz
        """
        current_freq_percore = []
        cpus = [cpu for cpu in os.listdir("/sys/devices/system/cpu") if re.match(r'\b(cpu)(\d+)\b',cpu)]
        for cpu in cpus:
            cmd = ["cat","/sys/devices/system/cpu/%s/cpufreq/scaling_cur_freq" % (cpu)]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            current_freq_percore.append(float(process.stdout.read().strip("\n"))/1000) # In MHz
        return current_freq_percore

    def get_current_freq_percore_by_cpuinfo(self):
        """Get current frequency CPU per core by cpuinfo file
           Return an int value in MHz
        """
        freq_percore = []
        with open("/proc/cpuinfo") as f:
            for line in f:
                if not line.startswith("cpu MHz"):
                    continue
                parts = line.split()
                freq_percore.append(float(parts[3]))

        return freq_percore

    def get_current_usage_mips(self):
         """Get current total usage CPU in MIPS
            Return an int value in MIPS
         """
         return sum(self.get_usage_mips_percore())

    # def get_busytime_percore(self):
#
#         global cpu_time  = [float(t[0])+float(t[2]) for t in psutil.cpu_times(percpu=True)]
#         time.sleep(interval)
#         cpu_time_t1  = [float(t[0])+float(t[2]) for t in psutil.cpu_times(percpu=True)]
#
#         # compute the delta time for each cpu and generate an list
#         busytime_percore = map(sub,cpu_time_t1,cpu_time_t0)
#
#         return busytime_percore

    def get_busytime_percore(self,interval=5):

        # cpu_time_t0  = [float(t[0])+float(t[2]) for t in psutil.cpu_times(percpu=True)]
        # time.sleep(interval)
        global cpu_time_percore
        cpu_time_t0   = cpu_time_percore
        cpu_time_t1  = [float(t[0])+float(t[2]) for t in psutil.cpu_times(percpu=True)]

        # compute the delta time for each cpu and generate an list
        busytime_percore = map(sub,cpu_time_t1,cpu_time_t0)
        cpu_time_percore = cpu_time_t1[:] # copy

        return busytime_percore


    def get_usage_mips_percore(self):
        """Returns an list with usage mips percore"""
        maxmips_percore               = self.get_max_mips_percore()
        maxfreq_percore               = self.get_max_freq_percore()
        currentfreq_percore           = self.get_current_freq_percore()
        utilized_cputime_percore      = self.get_busytime_percore()

        usage_percore = []

        for maxmips,maxfreq,currentfreq,utilized_cputime in zip(maxmips_percore,maxfreq_percore,currentfreq_percore,utilized_cputime_percore):
            usage_percore.append(int((((currentfreq * maxmips)/maxfreq) * utilized_cputime)))

        return usage_percore

    def get_usage_perc_percore(self):
        """Returns an list with usage percentual percore"""
        maxmips_percore    = get_max_mips_percore()
        usage_mips_percore = get_usage_mips_percore()

        usage_percore = []

        for maxmips,usage_mips in zip(maxmips_percore,usage_mips_percore):
            usage_percore.append(round((usage_mips * 100)/maxmips))

        return usage_percore

    def get_current_usage_mips(self):
        """Get current total usage CPU percentual
           Return an float value percentual
        """
        return sum(self.get_usage_mips_percore())

    def get_max_memory(self):
        """ Get max memory in MBytes
        """
        max_memory = int(psutil.virtual_memory().total)/1024**2
        return max_memory

    def get_used_memory(self):
        """ Get max memory in MBytes
        """
        used_memory = int(psutil.virtual_memory().used)/1024**2
        return used_memory

    def get_host_nic_speed(self,nic):
        """ Get current speed for informed NIC
            Return an int value in Mbits per second (Mb/s)
        """
        try:
            file_path = "/sys/class/net/%s/speed"  % (nic)
            nic_speed = open(file_path,"r").read().strip("\n")
            return int(nic_speed)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)

    def get_host_nic_rx_tx_bytes(self,nic):
        """ Get current status of Rx and Tx for informed NIC
            Return an dict of int value in bytes
        """
        nic_status = {}

        try:
            nic_status ['rx'] = open("/sys/class/net/%s/statistics/rx_bytes" % (nic),"r").read().strip("\n")
            nic_status ['tx'] = open("/sys/class/net/%s/statistics/tx_bytes" % (nic),"r").read().strip("\n")

            return nic_status
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)

    def get_hostname(self):
        """ Return Node Hostname
        """
        return socket.getfqdn()
