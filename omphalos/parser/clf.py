'''
Plugin to parse logs in CLF format
'''

import re
from datetime import datetime
from base import Parser
from base import Data

CLF_PARTS = [
    r'(?P<host>\S+)',
    r'\S+',
    r'(?P<user>\S+)',
    r'\[(?P<datetime>.+)\]',
    r'"(?P<method>\S+)',
    r'(?P<uri>\S+)',
    r'HTTP/(?P<version>.+)"',
    r'(?P<status>[0-9]+)',
    r'(?P<size>\S+)',
    r'"(?P<referer>.*)"',
    r'"(?P<agent>.*)"',
]

DATE_FORMAT = '%d/%b/%Y:%H:%M:%S'


class CLFParser(Parser):
    def __init__(self, logpath):
        '''
        Initialize the parser plugin

        @param logpath: Path the log file which is about to be parsed
        @type conf: C{str}
        '''
        self.clf_regex = re.compile(r'\s+'.join(CLF_PARTS) + r'\s*\Z')

    def parse_line(self, line):
        '''Parse a log line in Common Log Format and return the information'''

        match = self.clf_regex.match(line)
        if not match:
            return None

        fields = match.groupdict()

        # Adjust the time information
        # TODO: Adjust for timezone info
        timestamp, tz = fields.pop('datetime').split()
        fields['timestamp'] = datetime.strptime(timestamp, DATE_FORMAT)

        # Adjust other fields accordingly
        if fields['size'] == '-':
            fields['size'] = 0

        if fields['user'] == '-':
            fields['user'] = None

        if fields['referer'] == '-':
            fields['referer'] = None

        # Adjust the URI
        fields['uri'] = fields['uri'].replace('//', '/').split('/')
        fields['uri'] = '/'.join(fields['uri'][0:2])

        fields.pop('agent')
        fields.pop('host')
        fields.pop('version')

        return Data(**fields)

if __name__ == '__main__':
    import sys

    parser = CLFParser(sys.argv[1])

    with open(sys.argv[1]) as logfile:
        for line in logfile:
            print parser.parse_line(line)
