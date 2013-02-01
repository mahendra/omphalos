'''
Monitoring plugin which uses inotify to tail files
'''

import os
import time
import pyinotify

from monitor.base import Monitor

INOTIFY_MASK = pyinotify.IN_MODIFY | pyinotify.IN_DELETE_SELF


class FileMonitor(pyinotify.ProcessEvent):
    '''An event handler for monitoring log files'''

    def my_init(self, manager=None, transport=None, parser=None, path=None,
                monitor=None):
        '''Init function called by the constructor'''
        self.manager = manager
        self.transport = transport
        self.parser = parser
        self.path = path
        self.monitor = monitor
        self.fd = None
        self._register(path)

    def _register(self, path):
        '''Register for monitoring this file path'''
        try:
            if self.fd:
                self.fd.close()

            self.fd = open(path)

            # Read through the last 1kb of the file
            file_size = os.stat(path).st_size
            if file_size > 1024:
                self.fd.seek(-1024, 2)
        except OSError:
            self.monitor.notifier.stop()
            return

        self._process(path)
        self.manager.add_watch(path, INOTIFY_MASK, rec=False)

    def _process(self, path):
        # There is data to be read
        line = self.fd.readline()

        if not line:
            file_size = os.stat(path).st_size

            if file_size < self.fd.tell():
                # Looks the file has been truncated
                self.fd.seek(0)

        while line:
            data = self.parser.parse_line(line.strip())
            if data:
                self.transport.send(data)
            line = self.fd.readline()

    def process_IN_DELETE_SELF(self, event):
        '''Invoked if the file is deleted'''
        time.sleep(2)
        self._register(event.pathname)

    def process_IN_MODIFY(self, event):
        '''Invoked if the file is modified'''
        self._process(event.pathname)


class MonitorINotify(Monitor):
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

    def _check_exit(self, notifier):
        return self.check_exit()

    def run(self):
        '''
        Monitor the data source
        '''
        manager = pyinotify.WatchManager()
        fmonitor = FileMonitor(manager=manager, parser=self.parser,
                               path=self.file_path, transport=self.transport,
                               monitor=self)
        self.notifier = pyinotify.Notifier(manager, fmonitor)
        self.notifier.loop(self._check_exit)
