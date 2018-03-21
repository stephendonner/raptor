# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# simple local server on port 8000, to demonstrate
# receiving hero element timing results from a web extension

import BaseHTTPServer
import json
import os
import threading

from mozlog import get_proxy_logger

LOG = get_proxy_logger(component='control_server')


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        # get handler, received request for test settings from web ext runner
        self.send_response(200)
        validFiles = ['raptor-firefox-tp7.json',
                      'raptor-chrome-tp7.json',
                      'raptor-speedometer.json']
        head, tail = os.path.split(self.path)
        if tail in validFiles:
            LOG.info('reading test settings from ' + tail)
            try:
                with open(tail) as json_settings:
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(json.load(json_settings)))
                    self.wfile.close()
                    LOG.info('sent test settings to web ext runner')
            except Exception as ex:
                LOG.info('control server exception')
                LOG.info(ex)
        else:
            LOG.info('received request for unknown file: ' + self.path)

    def do_POST(self):
        # post handler, received results from web ext runner
        LOG.info("received test results")
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.getheader('content-length'))
        post_body = self.rfile.read(content_len)
        data = json.loads(post_body)
        LOG.info(data)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


class RaptorControlServer():
    """Container class for Raptor Control Server"""

    def __init__(self):
        self.raptor_venv = os.path.join(os.getcwd(), 'raptor-venv')
        self.server = None

    def start(self):
        here = os.getcwd()
        config_dir = os.path.join(here, 'raptor', 'tests')
        os.chdir(config_dir)
        server_address = ('', 8000)

        server_class = BaseHTTPServer.HTTPServer
        handler_class = MyHandler

        httpd = server_class(server_address, handler_class)

        server = threading.Thread(target=httpd.serve_forever)
        server.setDaemon(True)  # don't hang on exit
        server.start()
        LOG.info("raptor control server running on port 8000...")
        self.server = httpd

    def stop(self):
        LOG.info("shutting down control server")
        self.server.shutdown()
