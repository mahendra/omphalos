'''
The data structures required for colletor plugins
'''

from collections import namedtuple

# The response structure used by a plugin to return the summary
# of the data
Summary = namedtuple('Summary', ('hits', 'size', 'interval'))


class Collector(object):
    '''The base class for implementing a collector plugin'''
    def __init__(self, conf, timeout):
        '''
        Initialize the collector plugin

        @param conf: A configuration dictionary to be used by the plugin
        @type conf: C{dict}

        @param timeout: The time for which the data has to be stored
        @type timeout: C{int}
        '''
        pass

    def add_data(self, data):
        '''
        Add data to the collector

        @param data: The data that is being collected
        @type data: L{Data}
        '''
        raise NotImplemented('Not implemented in plugin')

    def get_summary(self):
        '''
        Get a summary of the collected data

        @return: The summary of the data
        @rtype: L{Summary}
        '''
        raise NotImplemented('Not implemented in plugin')

    def get_top(self, dtype, count):
        '''
        Get the top entries of a particular data set

        @param dtype: Must be 'hits', 'size', 'status', 'referer' or 'user'
        @type dtype: C{str}

        @param count: The top 'count' entries will be returned
        @type count: C{int}

        @return: A list of the most common entries and their counts
        @rtype: C{list}
        '''
        raise NotImplemented('Not implemented in plugin')
