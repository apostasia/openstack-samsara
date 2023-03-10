#!/bin/sh

# ansible version: 2.9.9
# vboxmanage version: 6.1.10
# vagrant version: 2.2.9

# create vagrant env
vagrant up --no-provision

# copy vagrant-ssh config to solve references in ansible playbook
vagrant ssh-config > ~/.ssh/config

#  create snapshot ubuntu  clean
vagrant snapshot save ubuntu-clean

# run ansible playbook - baremetal
ansible-playbook -i playbooks/openstack/hosts playbooks/openstack/playbook.yml

# Create snapshot OpenStack clean.
vagrant snapshot save openstack-clean

# run ansible playbook - vagrant
#ansible-playbook -i .vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory playbooks/openstack/playbook.yml 

# run ansible playbook - samsara
ansible-playbook -i playbooks/openstack/hosts playbooks/samsara/playbook.yml

# Create snapshot Samsara clean.
vagrant snapshot save samsara-clean
