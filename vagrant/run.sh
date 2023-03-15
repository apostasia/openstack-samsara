#!/bin/sh

# ansible version: 2.14.3
# vboxmanage version: 7.0.6
# vagrant version: 2.3.4

# create vagrant env
vagrant up --no-provision

#  create snapshot ubuntu  clean
vagrant snapshot save ubuntu-clean

# copy vagrant-ssh config to solve references in ansible playbook
vagrant ssh-config > ~/.ssh/config

# run ansible playbook - openstack install
ansible-playbook -i playbooks/openstack/hosts playbooks/openstack/playbook.yml

# Create snapshot OpenStack clean.
vagrant snapshot save openstack-clean

# run ansible playbook - setup cloud environment
 ansible-playbook -i playbooks/setup_cloud_env/hosts playbooks/setup_cloud_env/playbook.yml

# Create snapshot Cloud clean.
vagrant snapshot save cloud-clean

# run ansible playbook - samsara
ansible-playbook -i playbooks/samsara/hosts playbooks/samsara/playbook.yml

# Create snapshot Samsara clean.
vagrant snapshot save samsara-clean
