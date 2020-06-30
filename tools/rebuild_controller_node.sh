#!/bin/bash

# Update from repository
git pull

# Rebuild Samsara
sudo pip uninstall -y samsara
sudo rm -Rf build samsara.egg-info
sudo python setup.py build
sudo python setup.py install

# Remove Global Manager Init Scrip
sudo rm /etc/init/samsara-collector.conf
sudo rm /etc/init/samsara-local-controller.conf

# Reload Upstart Configuration
sudo initctl reload-configuration
