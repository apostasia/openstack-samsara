#!/bin/bash

sudo pip uninstall -y samsara
rm -Rf build samsara.egg-info
python setup.py build
sudo python setup.py install
