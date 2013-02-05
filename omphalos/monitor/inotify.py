'''
Monitoring plugin which uses inotify to tail files
'''

import os
import time
import pyinotify

from monitor.base import Monitor

INOTIFY_MASK = pyinotify.IN_MODIFY | pyinotify.IN_DELETE_SELF

# When a file is opened, read some data from the end of the file to
# ensure that we have not lost any data
READ_BACK = 1024


class FileMonitor(pyinotify.ProcessEvent):
    '''An event handler for monitoring log files'''

    def my_init(self, monitor=None):
        '''
        Init function called by the constructor

        @param monitor: The monitor plugin to be used
        @type paths: L{Monitor}
        '''
        self.monitor = monitor

    def process_IN_DELETE_SELF(self, event):
        '''Invoked if the file is deleted'''

        # TODO: The behaviour seems to have an issue. Not triggered always
        time.sleep(2)
        self.monitor.register(event.pathname)

    def process_IN_MODIFY(self, event):
        '''Invoked if the file is modified'''
        self.monitor.process(event.pathname)


class MonitorINotify(Monitor):
    '''The base class for implementing a monitoring plugin'''
    def __init__(self, conf, transport, parser, *paths):
        '''
        Initialize the monitoring plugin

        @param conf: A configuration dictionary to be used by the plugin
        @type conf: C{dict}

        @param transport: A transport instance used by the plugin
        @type conf: L{Transport}

        @param parser: A parser instance used by the plugin
        @type conf: L{Parser}

        @param paths: A list of paths to monitor
        @type paths: C{tuple}
        '''

        self.transport = transport
        self.parser = parser
        self.paths = list(paths)
        self.handles = {}

        if not self.paths:
            raise ValueError('At least one input file must be provided')

        # Initialize the monitors
        self.manager = pyinotify.WatchManager()
        self.monitor = FileMonitor(monitor=self)
        self.notifier = pyinotify.Notifier(self.manager, self.monitor)

        for path in self.paths:
            if not os.path.exists(path):
                raise ValueError('File does not exist: %s' % path)
            if not os.path.isfile(path):
                raise ValueError('Input is not a file: %s' % path)

            self.handles[path] = None
            self.register(path)

    def register(self, path):
        '''
        Register a file path for monitoring. Also, read the first few
        lines of data to ensure that we don't lose out on any data
        '''
        try:
            handle = self.handles[path]

            # Close the file handler first
            if handle:
                handle.close()
                self.handles[path] = None

            # Read through the last 1kb of the file
            handle = open(path, 'r')

            file_size = os.fstat(handle.fileno()).st_size
            if file_size > READ_BACK:
                handle.seek(-READ_BACK, 2)

            self.handles[path] = handle
        except IOError:
            self.exit()
            self.monitor.notifier.stop()
            return

        self.process(path)
        self.manager.add_watch(path, INOTIFY_MASK, rec=False)

    def process(self, path):
        # There is data to be read
        handle = self.handles[path]
        line = handle.readline()

        if not line:
            file_size = os.fstat(handle.fileno()).st_size

            if file_size < handle.tell():
                # Looks the file has been truncated
                handle.seek(0)

        while line:
            data = self.parser.parse_line(line.strip())
            if data:
                self.transport.send(data)
            line = handle.readline()

    def _check_exit(self, notifier):
        return self.check_exit()

    def run(self):
        '''
        Monitor the data source
        '''
        self.notifier.loop(self._check_exit)
