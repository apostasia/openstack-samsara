#!/usr/bin/env python
# coding: utf-8

from oslo_config import cfg
import oslo_messaging as messaging
import logging
import psutil
import time

logging.basicConfig()
log = logging.getLogger()

log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

transport_url = 'rabbit://guest:guest@10.0.1.20:5672/'
transport = messaging.get_transport(cfg.CONF, transport_url)

driver = 'messaging'

notifier = messaging.Notifier(transport, driver=driver, publisher_id='testing', topic='monitor')

while True:
    
    cpu_load = psutil.cpu_percent()
    notifier.info({'CPU LOAD': cpu_load, 'ram': 90}, 'just.testing', {'heavy': 'payload'})
    time.sleep(5)