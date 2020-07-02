#!/bin/bash

sudo pip3 uninstall -y samsara
rm -Rf build samsara.egg-info
python3 setup.py build
sudo python3 setup.py install
