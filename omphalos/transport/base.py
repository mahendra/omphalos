'''
The data structures required for transport plugins
'''


class Transport(object):
    '''The base class for implementing a collector plugin'''
    def __init__(self, conf):
        '''
        Initialize the transport plugin

        @param conf: A configuration dictionary to be used by the plugin
        @type conf: C{dict}
        '''
        pass

    def send(self, data):
        '''
        Send data on the transport

        @param data: The data that is being collected
        @type data: L{Data}
        '''
        raise NotImplemented('Not implemented in plugin')

    def recv(self):
        '''
        Get data from the transport

        @return: The first entry available in the queue
        @rtype: L{Data}
        '''
        raise NotImplemented('Not implemented in plugin')
