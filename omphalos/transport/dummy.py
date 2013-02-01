'''
A dummy tranport which is useful for local apps
'''

from base import Transport


class Dummy(Transport):
    '''The base class for implementing a collector plugin'''
    def __init__(self, conf=None, collector=None):
        '''
        Initialize the transport plugin

        @param conf: A configuration dictionary to be used by the plugin
        @type conf: C{dict}

        @param collector: A collector instance for sending data to
        @type collector: L{Collector}
        '''
        self.collector = collector

    def send(self, data):
        '''
        Send data on the transport

        @param data: The data that is being collected
        @type data: L{Data}
        '''
        self.collector.add_data(data)
