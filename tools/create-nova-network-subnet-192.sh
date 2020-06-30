#!/bin/bash


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

nova network-delete $(nova network-list |grep net | cut -d"|" -f2)
nova network-create cloud-samsara-subnet --bridge br100 --multi-host T --fixed-range-v4 192.168.0.0/24

nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0
nova secgroup-add-rule default tcp 22 22 0.0.0.0/0

nodes=(10.0.1.21 10.0.1.22 10.0.1.23 10.0.1.24)

for node in ${nodes[@]}
do
    echo "[+] Kill dnsmasq at ($node)"
    sshpass -p lups999 ssh lups@$node 'sudo killall dnsmasq'

    echo "[+] Restart nova-network at ($node)"
    sshpass -p lups999 ssh lups@$node 'sudo service nova-network restart'


done
