from os.path import join, abspath, dirname

import os
import sys

# Path definition
current_dir = abspath(dirname(__file__))
PROJECT_ROOT =  current_dir.split('/')
PROJECT_ROOT.pop(3) # remove mailsync, that's our namespace
PROJECT_ROOT = "/".join(PROJECT_ROOT)

sys.path.insert(0, PROJECT_ROOT)

import tornado.ioloop
import tornado.httpserver
import tornado.web
from tornado import autoreload
from mailsync.app import application

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(4321)
    ioloop = tornado.ioloop.IOLoop().instance()
    autoreload.start(ioloop)
    ioloop.start()