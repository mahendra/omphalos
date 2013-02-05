'''
Plugin to parse logs in W3C log format
'''

import re
from datetime import datetime
from base import Parser
from base import Data

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class W3CLogParser(Parser):
    def __init__(self, logpath):
        '''
        Initialize the parser plugin

        @param logpath: Path the log file which is about to be parsed
        @type conf: C{str}
        '''

        fields = []

        with open(logpath) as logfile:
            for line in logfile:
                if line.startswith('#Fields'):
                    fields = line.strip().split(' ')[1:]
                    break

        if not fields:
            raise RuntimeError('Unable to determine logfile format')

        parts = []
        for field in fields:
            field = field.replace('(', '-').replace(')', '-').lower()
            field = field.replace('-', '_')
            part = r'(?P<%s>\S+)' % (field)
            parts.append(part)

        self.w3c_regex = re.compile(r'\s+'.join(parts) + r'\s*\Z')

    def parse_line(self, line):
        '''Parse a log line in Common Log Format and return the information'''

        match = self.w3c_regex.match(line)
        if not match:
            return None

        fields = match.groupdict()

        # Adjust the time information
        timestamp = '%s %s' % (fields['date'], fields['time'])
        timestamp = datetime.strptime(timestamp, DATE_FORMAT)

        # Adjust other fields accordingly
        if 'size' not in fields:
            fields['size'] = 0

        if fields.get('cs_username', '-') == '-':
            fields['cs_username'] = None

        if fields.get('sc_referer', '-') == '-':
            fields['sc_referer'] = None

        # Adjust the URI
        if 'cs_uri_stem' in fields:
            uri = fields.pop('cs_uri_stem')
        else:
            uri = fields.pop('cs_uri')

        uri = uri.replace('//', '/').split('/')
        uri = '/'.join(uri[0:2])

        return Data(uri=uri, timestamp=timestamp, size=fields['size'],
                    status=fields['sc_status'],
                    method=fields['cs_method'],
                    referer=fields['sc_referer'],
                    user=fields['cs_username'])

if __name__ == '__main__':
    import sys

    parser = W3CLogParser(sys.argv[1])

    with open(sys.argv[1]) as logfile:
        for line in logfile:
            print parser.parse_line(line)
