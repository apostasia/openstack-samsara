#!/bin/bash

ls /etc/init/samsara-* | cut -d '/' -f4 | cut -d '.' -f1 | while read S; do sudo start $S; done
