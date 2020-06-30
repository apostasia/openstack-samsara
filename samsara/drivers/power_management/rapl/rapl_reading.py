# -*- coding: latin1 -*-
import sys
import math
import re
import time
from binascii import hexlify
# abrindo o arquivo msr
# caso nao esteje ativo habilitar usando:
# sudo modprobe msr

MSR_RAPL_POWER_UNIT = 0x606     # mas um #define a la modo C bem bagual

#Package RAPL Domain */
MSR_PKG_RAPL_POWER_LIMIT =  0x610
MSR_PKG_ENERGY_STATUS = 0x611
MSR_PKG_PERF_STATUS = 0x613
MSR_PKG_POWER_INFO = 0x614

#PP0 RAPL Domain */
MSR_PP0_POWER_LIMIT = 0x638
MSR_PP0_ENERGY_STATUS = 0x639
MSR_PP0_POLICY = 0x63A
MSR_PP0_PERF_STATUS = 0x63B

#PP1 RAPL Domain, may reflect to uncore devices */
MSR_PP1_POWER_LIMIT = 0x640
MSR_PP1_ENERGY_STATUS = 0x641
MSR_PP1_POLICY = 0x642

#DRAM RAPL Domain
MSR_DRAM_POWER_LIMIT = 0x618
MSR_DRAM_ENERGY_STATUS = 0x619
MSR_DRAM_PERF_STATUS = 0x61B
MSR_DRAM_POWER_INFO = 0x61C

#RAPL UNIT BITMASK
POWER_UNIT_OFFSET = 0
POWER_UNIT_MASK = 0x0F

ENERGY_UNIT_OFFSET = 0x08
ENERGY_UNIT_MASK = 0x1F00

TIME_UNIT_OFFSET = 0x10
TIME_UNIT_MASK = 0xF000

# defines para detectar o modelo de CPU
CPU_SANDYBRIDGE =    "42"
CPU_SANDYBRIDGE_EP = "45"
CPU_IVYBRIDGE =      "58"
CPU_IVYBRIDGE_EP =   "62"
CPU_HASWELL =        "60"
CPU_HASWELL_EP =     "63"
CPU_BROADWELL =      "61"

def detect_cpu():
    procFile = open('/proc/cpuinfo','r')
    procFile.readline()
    isGenuine = procFile.readline()
    if re.search('GenuineIntel',isGenuine):
        print "Processador Intel Genuine\n"
    else:
        print "Não é um processador intel, sorry\n"

    family = procFile.readline()
    if re.sub('[A-z]*\s*:*','',family) == "6":
        print "Familia correta"
    else:
        print "Familia desconhecida"
        return None

    modelo = procFile.readline()
    aux = re.sub('[A-z]*\s*:*','',modelo)
    if aux == CPU_SANDYBRIDGE:
        print "Modelo Sandybridge"
    elif aux == CPU_SANDYBRIDGE_EP:
        print "Modelo Sandybridge EP"
    else:
        print "Unsupported model %s" % aux
        return None
    procFile.close()
    return aux

#função para ler o registradores msr
def read_msr(file, offset):
    msrFile = open('/dev/cpu/0/msr','rb')
    msrFile.seek(offset,0)
    t = msrFile.read(8)     # o arquivo em c lia 64bits, mative isso hehe
    hex = hexlify(t[::-1])  # tem que inverter o string lido porque a disgrama é little endian
                            # motivo pelo qual eu não sei. mas me consumiu um bom tempo ate pescar
    return int(hex,16)



# aqui começa o codigo de leitura
print "---------------------------------------------------------\n"
cpu_model = detect_cpu()
print cpu_model
msrFile = open('/dev/cpu/0/msr','rb')
result = read_msr(msrFile,MSR_RAPL_POWER_UNIT)
power_units=pow(0.5,result&0xf)
cpu_energy_units=pow(0.5,(result>>8)&0x1f)
time_units=pow(0.5,(result>>16)&0xf)

if cpu_model==CPU_HASWELL_EP:
    dram_energy_units=pow(0.5,16)
else:
    dram_energy_units=cpu_energy_units

#cpu_energy_units=pow(0.5,(double)((result>>8)&0x1f));
#	time_units=pow(0.5,(double)((result>>16)&0xf));

print "Power Unit = %.3f Watts" % power_units
print "CPU energy units = %.8fJ" % cpu_energy_units
print "DRAM Energy units = %.8fJ" % dram_energy_units
print "Time units = %.8fs" % time_units

result = read_msr(msrFile,MSR_PKG_POWER_INFO)
thermal_spec_power=power_units*(result&0x7fff)
minimum_power=power_units*((result>>16)&0x7fff)
maximum_power=power_units*((result>>32)&0x7fff)
time_window=time_units*((result>>48)&0x7fff)

print ""
print "Package thermal spec: %.3fW" % thermal_spec_power
print "Package minimum power: %.3fW" % minimum_power
print "Package maximum power: %.3fW" % maximum_power
print "Package maximum time window: %.6fs" % time_window


result = read_msr(msrFile,MSR_PKG_RAPL_POWER_LIMIT)
pkg_power_limit_1 = power_units*((result>>0)&0x7FFF)
pkg_time_window_1 = time_units*((result>>17)&0x007F)
pkg_power_limit_2 = power_units*((result>>32)&0x7FFF)
pkg_time_window_2 = time_units*((result>>49)&0x007F)

# essa caracteristica eu não sei se está correta
print "Package power limits are %s" % ("locked" if (result >> 63) else "unlocked")
#===============================================================

print "Package power limit #1: %.3fW for %.6fs (%s, %s)" % (pkg_power_limit_1, pkg_time_window_1, ("enable" if result&(1<<15) else "disable"),("clamped" if result&(1<<16) else "not_clamped"))
print "Package power limit #2: %.3fW for %.6fs (%s, %s)" % (pkg_power_limit_2, pkg_time_window_2, ("enable" if result&(1<<47) else "disable"),("clamped" if result&(1<<48) else "not_clamped"))


#lendo o consumo de energia total
print ""
result=read_msr(msrFile,MSR_PKG_ENERGY_STATUS)
package_before=result*cpu_energy_units
print "Package energy before: %.6fJ" % package_before

if ((cpu_model==CPU_SANDYBRIDGE_EP) or (cpu_model==CPU_IVYBRIDGE_EP)):
    result = read_msr(msrFile,MSR_PKG_PERF_STATUS)
    acc_pkg_throttled_time = result*time_units;
    print "Accumulated Package Throttled Time : %.6fs" % acc_pkg_throttled_time

result = read_msr(msrFile,MSR_PP0_ENERGY_STATUS);
pp0_before = result*cpu_energy_units;
print "PowerPlane0 (core) for core 0 energy before: %.6fJ" % pp0_before
result = read_msr(msrFile,MSR_PP0_POLICY);
pp0_policy = result&0x001f;
print "PowerPlane0 (core) for core 0 policy: %d" % pp0_policy

if (cpu_model==CPU_SANDYBRIDGE_EP) or (cpu_model==CPU_IVYBRIDGE_EP):
    result = read_msr(msrFile,MSR_PP0_PERF_STATUS)
    acc_pp0_throttled_time = result*time_units
    print "PowerPlane0 (core) Accumulated Throttled Time: %.6fs" % acc_pp0_throttled_time

if (cpu_model==CPU_SANDYBRIDGE) or (cpu_model==CPU_IVYBRIDGE) or (cpu_model==CPU_HASWELL):
    result=read_msr(msrFile,MSR_PP1_ENERGY_STATUS)
    pp1_before = result*cpu_energy_units
    print "PowerPlane1 (on-core GPU if avail) before: %.6fJ" % pp1_before
    result = read_msr(msrFile,MSR_PP1_POLICY)
    pp1_policy = result&0x001f
    print "PowerPlane1 (on-core GPU if avail) 0 policy: %d" % pp1_policy

if (cpu_model==CPU_SANDYBRIDGE_EP) or (cpu_model==CPU_IVYBRIDGE_EP) or (cpu_model==CPU_HASWELL_EP) or (cpu_model==CPU_HASWELL) or (cpu_model==CPU_BROADWELL):
    result = read_msr(msrFile,MSR_DRAM_ENERGY_STATUS)
    dram_before = result*dram_energy_units
    print "DRAM energy before: %.6fJ" % dram_before

print "\nSleeping 1 second\n\n"
time.sleep(1)

result=read_msr(msrFile,MSR_PKG_ENERGY_STATUS)
package_after=result*cpu_energy_units;
print "Package energy after: %.6f  (%.6fJ consumed)" % (package_after,package_after-package_before)

result = read_msr(msrFile,MSR_PP0_ENERGY_STATUS)
pp0_after = result*cpu_energy_units
print "PowerPlane0 (core) for core 0 energy after: %.6f (%.6fJ consumed)" % (pp0_after,pp0_after-pp0_before)
#not available on SandyBridge-EP */
if (cpu_model==CPU_SANDYBRIDGE) or (cpu_model==CPU_IVYBRIDGE) or (cpu_model==CPU_HASWELL):
    result = read_msr(msrFile,MSR_PP1_ENERGY_STATUS)
    pp1_after = result*cpu_energy_units
    print "PowerPlane1 (on-core GPU if avail) after: %.6f (%.6fJ consumed)" % (pp1_after,pp1_after-pp1_before)

if (cpu_model==CPU_SANDYBRIDGE_EP) or (cpu_model==CPU_IVYBRIDGE_EP) or (cpu_model==CPU_HASWELL_EP) or (cpu_model==CPU_HASWELL) or (cpu_model==CPU_BROADWELL):
    result = read_msr(msrFile,MSR_DRAM_ENERGY_STATUS)
    dram_after = result*dram_energy_units
    print "DRAM energy after: %.6f  (%.6fJ consumed)" % (dram_after,dram_after-dram_before)

print ""
print "Note: the energy measurements can overflow in 60s or so"
print "      so try to sample the counters more often than that."


msrFile.close()
print "---------------------------------------------------------\n"
