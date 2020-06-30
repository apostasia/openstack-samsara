#!/bin/bash

# Update from repository
git pull

# Rebuild Samsara
sudo pip uninstall -y samsara
rm -Rf build samsara.egg-info
python setup.py build
sudo python setup.py install

# Remove Global Manager Init Scrip
sudo rm /etc/init/samsara-global-controller.conf

# Reload Upstart Configuration
sudo initctl reload-configuration
