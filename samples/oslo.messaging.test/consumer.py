#!/usr/bin/env python
# coding: utf-8

from oslo_config import cfg
import oslo_messaging as messaging
import logging

import eventlet

eventlet.monkey_patch()

logging.basicConfig()
log = logging.getLogger()

log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

class NotificationHandler(object):
    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        if publisher_id == 'testing':
            log.info('Handled'+str(ctxt))
            return messaging.NotificationResult.HANDLED
            
        if publisher_id == 'planning':
            log.info('Planning'+str(ctxt))
            return messaging.NotificationResult.HANDLED

    def warn(self, ctxt, publisher_id, event_type, payload, metadata):
        log.info('WARN')

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        log.info('ERROR')

log.info('Configuring connection')
transport_url = 'rabbit://guest:guest@10.0.1.20:5672/'
transport = messaging.get_transport(cfg.CONF, transport_url)

targets = [messaging.Target(topic='monitor')]
endpoints = [NotificationHandler()]

server = messaging.get_notification_listener(transport, targets, endpoints, allow_requeue=True, executor='eventlet')
log.info('Starting up server')
server.start()
log.info('Waiting for something')
server.wait()
