'''
Monitoring plugin which polls the files at fixed intervals
'''

import os
import time

from monitor.base import Monitor


class Poll(Monitor):
    '''The base class for implementing a monitoring plugin'''
    def __init__(self, conf, transport, parser):
        '''
        Initialize the monitoring plugin

        @param conf: A configuration dictionary to be used by the plugin
        @type conf: C{dict}

        @param transport: A transport instance used by the plugin
        @type conf: L{Transport}

        @param parser: A parser instance used by the plugin
        @type conf: L{Parser}
        '''

        self.file_path = conf['file_path']
        self.transport = transport
        self.parser = parser
        self.poll = 5
        self._register()

    def _register(self):
        '''Register for polling the file'''
        try:
            self.fd = open(self.file_path)

            # Read through the last 1kb of the file
            file_size = os.stat(self.file_path).st_size
            if file_size > 1024:
                self.fd.seek(-1024, 2)
        except OSError:
            self.exit()

    def run(self):
        '''
        Monitor the data source
        '''
        while not self.check_exit():
            line = self.fd.readline()

            if not line:
                try:
                    file_size = os.stat(self.file_path).st_size
                except OSError:
                    return

                if file_size < self.fd.tell():
                    # Looks the file has been truncated
                    self._register()

            while line:
                data = self.parser.parse_line(line.strip())
                if data:
                    self.transport.send(data)
                line = self.fd.readline()

            time.sleep(self.poll)
