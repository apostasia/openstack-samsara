#!/bin/bash

ls /etc/init/nova-* | cut -d '/' -f4 | cut -d '.' -f1 | while read S; do sudo stop $S; done
