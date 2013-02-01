'''
The data structures required for output plugins
'''


class Output(object):
    '''The base class for implementing a collector plugin'''
    def __init__(self, conf, collector):
        '''
        Initialize the output plugin

        @param conf: A configuration dictionary to be used by the plugin
        @type conf: C{dict}

        @param collector: A collector instance used by the plugin
        @type conf: L{Collector}
        '''
        pass

    def run(self):
        '''
        Process data from the collector continuously
        '''
        raise NotImplemented('Not implemented in plugin')

    def exit(self):
        '''Indicate that the display must stop'''
        self._exit = True

    def check_exit(self):
        '''Used for checking if the the display must stop'''

        if not hasattr(self, '_exit'):
            self._exit = False
        return self._exit
