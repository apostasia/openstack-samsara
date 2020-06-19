#!/bin/sh

# ansible version: 2.9.9
# vboxmanage version: 6.1.10
# vagrant version: 2.2.9

# create vagrant env
vagrant up

# copy vagrant-ssh config to solve references in ansible playbook
vagrant ssh-config > ~/.ssh/config

#  create snapshot ubuntu  clean
#vagrant snapshot save ubuntu-clean

# run ansible playbook - baremetal
ansible-playbook -i playbooks/openstack/hosts playbooks/openstack/playbook.yml 

# run ansible playbook - vagrant
#ansible-playbook -i .vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory playbooks/openstack/playbook.yml 
