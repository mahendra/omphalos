'''
The data structures required parsers
'''

from common.base import Data


class Parser(object):
    '''The base class for implementing a parser plugin'''
    def __init__(self, logpath):
        '''
        Initialize the parser plugin

        @param logpath: Path the log file which is about to be parsed
        @type conf: C{str}
        '''
        pass

    def parse_line(self, line):
        '''
        Parse a line in the log file and return the Data

        @param line: The line that is being parsed
        @type line: C{str}

        @return: The parsed data
        @rtype: L{Data}
        '''
        raise NotImplemented('Not implemented in plugin')
