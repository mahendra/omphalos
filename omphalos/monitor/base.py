'''
The data structures required for monitoring plugins
'''


class Monitor(object):
    '''The base class for implementing a monitoring plugin'''
    def __init__(self, conf, transport):
        '''
        Initialize the monitoring plugin

        @param conf: A configuration dictionary to be used by the plugin
        @type conf: C{dict}

        @param transport: A transport instance used by the plugin
        @type conf: L{Transport}
        '''
        pass

    def run(self):
        '''
        Monitor the data source
        '''
        raise NotImplemented('Not implemented in plugin')

    def exit(self):
        '''Indicate that the monitor must exit'''
        self._exit = True

    def check_exit(self):
        '''Used for checking if the the monitor must exit'''

        if not hasattr(self, '_exit'):
            self._exit = False
        return self._exit
