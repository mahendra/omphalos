#!/usr/bin/env python
'''
A command line utility for monitoring traffic on a machine by
following data on the http log file
'''

import cement
import sys
import threading
import time

from monitor.inotify import MonitorINotify
from monitor.poll import Poll
from collector.slider import Slider
from output.console import Console
from parser.clf import CLFParser
from parser.w3c import W3CLogParser
from transport.dummy import Dummy

try:
    from cement.core import foundation, controller, handler, exc
except ImportError:
    print('cement module is mandatory for running commands')
    sys.exit(-1)

class HttpTopController(controller.CementBaseController):
    class Meta:
        label = 'base'
        description = 'Command for monitoring HTTP traffic'

        arguments = [
            (['-p', '--parser'], dict(action='store', dest='parser',
                                      default='clf',
                              help='The parser to use: clf/w3c')),

            (['-i', '--interval'], dict(action='store', dest='interval',
                                        default=120, type=int,
                              help='The time period for storing data')),

            (['-r', '--refresh'], dict(action='store', dest='refresh_time',
                                       default=10, type=int,
                              help='Screen refresh interval')),

            (['-c', '--count'], dict(action='store', dest='top_count',
                                     default=12, type=int,
                              help='Number of top entries to display')),

            (['--total-size'], dict(action='store', dest='total_size',
                                    default=0, type=int,
                              help='Total traffic for generating alerts')),

            (['--total-hits'], dict(action='store', dest='total_hits',
                                    default=0, type=int,
                              help='Total hits for generating alert')),

            (['--size'], dict(action='store', dest='size', default=0, type=int,
                              help='Per segment traffic to generate an alert')),

            (['--hits'], dict(action='store', dest='hits', default=0, type=int,
                              help='Per segment hits to generate an alert')),

            (['log_file'], dict(action='store',
                                help='The log file to monitor')),
        ]

    @controller.expose(hide=True, aliases=['run'])
    def default(self):
        '''
        Run the httptop command
        '''

        # Start the sliding collector with 2 minutes of storage
        conf = {}
        collector = Slider(conf, self.pargs.interval)

        # Start a dummy transport
        transport = Dummy(collector=collector)

        # Start the parser
        if self.pargs.parser == 'clf':
            parser = CLFParser(self.pargs.log_file)
        elif self.pargs.parser == 'w3c':
            parser = W3CLogParser(self.pargs.log_file)
        else:
            raise ValueError('Invalid parser')

        # Start the monitor
        monitor = MonitorINotify(conf, transport, parser, self.pargs.log_file)

        # Switch to this for use on Linux, Windows or Mac (to be tested)
        # monitor = Poll(conf, transport, parser)

        # Start the console display
        displayconf = {
            'refresh_time': self.pargs.refresh_time,
            'top_count': self.pargs.top_count,
            'alerts': {
                'total_size': self.pargs.total_size,
                'total_hits': self.pargs.total_hits,
                'size': self.pargs.size,
                'hits': self.pargs.hits
            },
        }

        display = Console(displayconf, collector)

        # Start two threads. One for monitoring and one for displaying
        # on the console
        try:
            monitor_th = threading.Thread(target=monitor.run)
            display_th = threading.Thread(target=display.run)
            monitor_th.daemon = True
        except Exception:
            print('Error in running app')
            sys.exit(-1)

        monitor_th.start()
        display_th.start()

class HttpTopApp(foundation.CementApp):
    class Meta:
        label = 'httptop'
        base_controller = HttpTopController

app = HttpTopApp()

try:
    app.setup()
    app.run()
except Exception as exp:
    print('ERROR: %s' % str(exp))
finally:
    app.close()
