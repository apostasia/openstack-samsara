#!/bin/bash

#
# Inicializa o data-collector em todos os compute nodes
#
echo "+--------------------------------------------------------------+"
echo "|                  Sincronizando nodos                         |"
echo "+--------------------------------------------------------------+"

echo "[+] controller"
sudo service ntp restart
date
echo  " "

echo "[+] compute-001"
sshpass -p lups999 ssh lups@10.0.1.21 'sudo /etc/init.d/ntp restart;date'
echo  " "

echo "[+] compute-002"
sshpass -p lups999 ssh lups@10.0.1.22 'sudo /etc/init.d/ntp restart;date'
echo  " "

echo "[+] compute-003"
sshpass -p lups999 ssh lups@10.0.1.23 'sudo /etc/init.d/ntp restart;date'
echo  " "

echo "[+] compute-004"
sshpass -p lups999 ssh lups@10.0.1.24 'sudo /etc/init.d/ntp restart;date'

# To use an OpenStack cloud you need to authenticate against the Identity
# service named keystone, which returns a **Token** and **Service Catalog**.
# The catalog contains the endpoints for all services the user/tenant has
# access to - such as Compute, Image Service, Identity, Object Storage, Block
# Storage, and Networking (code-named nova, glance, keystone, swift,
# cinder, and neutron).
#
# *NOTE*: Using the 2.0 *Identity API* does not necessarily mean any other
# OpenStack API is version 2.0. For example, your cloud provider may implement
# Image API v1.1, Block Storage API v2, and Compute API v2.0. OS_AUTH_URL is
# only for the Identity API served through keystone.
export OS_AUTH_URL=http://controller:35357/v3

# With the addition of Keystone we have standardized on the term **tenant**
# as the entity that owns the resources.
unset OS_TENANT_ID
unset OS_TENANT_NAME
unset OS_PROJECT_NAME
unset OS_PROJECT_DOMAIN_ID
unset OS_USER_DOMAIN_ID
unset OS_USERNAME

export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_ID=default
export OS_PROJECT_NAME=admin
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://controller:35357/v3



# In addition to the owning entity (tenant), OpenStack stores the entity
# performing the action as the **user**.
export OS_USERNAME="admin"

# With Keystone you pass the keystone password.
#echo "Please enter your OpenStack Password: "
#read -sr OS_PASSWORD_INPUT
#export OS_PASSWORD=$OS_PASSWORD_INPUT
export OS_PASSWORD="samsara"

# If your configuration has multiple regions, we set that information here.
# OS_REGION_NAME is optional and only valid in certain environments.
export OS_REGION_NAME="RegionOne"
# Don't leave a blank variable, unset it if it was empty
if [ -z "$OS_REGION_NAME" ]; then unset OS_REGION_NAME; fi

echo "+--------------------------------------------------------------+"
echo "|           Samsara: Parando os Serviços Locais                |"
echo "+--------------------------------------------------------------+"

echo "[+] compute-001"
sshpass -p lups999 ssh lups@10.0.1.21 'sudo stop samsara-local-controller'
sshpass -p lups999 ssh lups@10.0.1.21 'sudo stop samsara-collector'

echo "[+] compute-002"
sshpass -p lups999 ssh lups@10.0.1.22 'sudo stop samsara-local-controller'
sshpass -p lups999 ssh lups@10.0.1.22 'sudo stop samsara-collector'

echo "[+] compute-003"
sshpass -p lups999 ssh lups@10.0.1.23 'sudo stop samsara-local-controller'
sshpass -p lups999 ssh lups@10.0.1.23 'sudo stop samsara-collector'

echo "[+] compute-004"
sshpass -p lups999 ssh lups@10.0.1.24 'sudo stop samsara-local-controller'
sshpass -p lups999 ssh lups@10.0.1.24 'sudo stop samsara-collector'

echo "+--------------------------------------------------------------+"
echo "|           Samsara: Parando Global Controller                 |"
echo "+--------------------------------------------------------------+"

sudo stop samsara-global-controller

echo "+--------------------------------------------------------------+"
echo "|           Samsara: Limpando Base de Dados                    |"
echo "+--------------------------------------------------------------+"

sudo su - postgres -c "psql -d samsara -c \"TRUNCATE cell_energy_consumption, cell_events, cell_situation, historical_host_situation, host_events, host_info, host_resources_usage, host_situation, migration_events RESTART IDENTITY;\""

#
# Cria vms no compute
#
echo "+--------------------------------------------------------------+"
echo "|           Nova: Criando a Máquinas Virtuais                  |"
echo "+--------------------------------------------------------------+"

i=1
for i in {1..30}
do
    nova boot --flavor m2.tiny --image samsara-soul-2hours --nic net-id=8e37a407-b6ad-4386-926b-6b13bf7324bf \
        --security-group default --key-name vilnei_at_lups `printf samsara-soul-2hours-%02d $i` > /dev/null
done

sleep 10s
nova list

echo "+--------------------------------------------------------------+"
echo "|           Samsara: Iniciando Global Controller                |"
echo "+--------------------------------------------------------------+"

sudo start samsara-global-controller


echo "+--------------------------------------------------------------+"
echo "|           Samsara: Iniciando os Serviços Locais              |"
echo "+--------------------------------------------------------------+"

echo "[+] compute-001"
sshpass -p lups999 ssh lups@10.0.1.21 'sudo start samsara-collector'
sshpass -p lups999 ssh lups@10.0.1.21 'sudo start samsara-local-controller'


echo "[+] compute-002"
sshpass -p lups999 ssh lups@10.0.1.22 'sudo start samsara-collector'
sshpass -p lups999 ssh lups@10.0.1.22 'sudo start samsara-local-controller'

echo "[+] compute-003"
sshpass -p lups999 ssh lups@10.0.1.23 'sudo start samsara-collector'
sshpass -p lups999 ssh lups@10.0.1.23 'sudo start samsara-local-controller'

echo "[+] compute-004"
sshpass -p lups999 ssh lups@10.0.1.24 'sudo start samsara-collector'
sshpass -p lups999 ssh lups@10.0.1.24 'sudo start samsara-local-controller'

echo "+--------------------------------------------------------------+"
echo "|           Experimento: Status                                |"
echo "+--------------------------------------------------------------+"

CURRENT_TIME=$(date -u)
PREV_LOCAL=$(date -d "now 120 minutes")
PREV_UTC=$(date -u -d "now 120 minutes")

echo "Relógio Atual (UTC): $CURRENT_TIME"

echo "Previsão de término"
echo "Horário Local: $PREV_LOCAL"
echo "Horário UTC: $PREV_UTC"
