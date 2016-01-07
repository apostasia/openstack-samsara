# from subprocess import *
# from multiprocessing.managers import BaseManager
# process = Popen(["rootwrap-daemon", "rootwrap.conf"], stdout=PIPE)
# address = process.stdout.readline()[:-1].decode('utf-8')
# authkey = process.stdout.read(32)
#
# class MyManager(BaseManager): pass
#
# MyManager.register("rootwrap")
# from oslo.rootwrap import client  # to set up 'jsonrpc' serializer only
# manager = MyManager(address, authkey, serializer='jsonrpc')
# manager.connect()
# proxy = manager.rootwrap()
# proxy.run_one_command(["cat"], stdin="Hello, world!")
#
# [0, u'Hello, world!', u'']
# process.kill()
