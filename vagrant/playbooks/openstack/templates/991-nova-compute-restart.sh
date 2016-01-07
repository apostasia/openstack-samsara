#!/bin/bash

sudo /etc/init.d/networking stop
sudo /etc/init.d/networking start

sudo service dbus restart
sudo service libvirt-bin restart

# Reiniciando OpenStack Nova Compute
sudo service dbus restart
sudo service libvirt-bin restart
ls /etc/init/nova-* | cut -d '/' -f4 | cut -d '.' -f1 | while read S; do sudo stop $S; done
ls /etc/init/nova-* | cut -d '/' -f4 | cut -d '.' -f1 | while read S; do sudo start $S; done
sudo service nova-compute restart
sudo service nova-network restart
sudo service nova-api-metadata restart
