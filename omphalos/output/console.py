'''
Output plugin to display the data on a console
'''

import curses
from collections import Counter
from output.base import Output

HELP_STR = 'Keys: (h) Hits, (b) Bytes, (r) Referers, (u) Users, (q) Quit'
HELP_STR = HELP_STR.ljust(79)

ALERT_NONE = 1
ALERT_PRINT = 2
ALERT_CLEAR = 3

FORMAT_INFO = {
    'hits': ('%-30s\t%10s\t%15s' % ('Top URIs by hits', 'Hits', 'Bytes'),
             '%-30s\t%10d\t%15d'),
    'size': ('%-30s\t%10s\t%15s' % ('Top URIs by traffic', 'Bytes', 'Hits'),
             '%-30s\t%10d\t%15d'),
    'referer': ('%-40s\t%10s' % ('Top Referrers', 'Hits'), '%-40s\t%10d'),
    'user': ('%-30s\t%10s' % ('Top Users', 'Hits'), '%-30s\t%10d')
}


class Console(Output):
    '''The base class for implementing a collector plugin'''
    def __init__(self, conf, collector):
        '''
        Initialize the console output plugin

        @param conf: A configuration dictionary to be used by the plugin
        @type conf: C{dict}
        '''
        conf = conf if conf else {}

        self.refresh = conf.get('refresh_time', 5)
        self.top_count = conf.get('top_count', 15)
        self.alerts = conf.get('alerts', {})

        # We have limited space in the screen. Let us limit the display
        if self.top_count > 15:
            self.top_count = 15

        self.collector = collector

    def run(self):
        '''
        Process data from the collector continuously and display on console
        '''
        # Run the display program within the curses wrapper
        curses.wrapper(self._display)

    def _display(self, stdscr):
        '''
        Process data from the collector continuously and display on console

        @param stdscr: The curses window object
        @type conf: L{curses.window}
        '''

        refresh_time = 100 if self.refresh > 10 else (self.refresh * 10)
        curses.halfdelay(refresh_time)

        curses.use_default_colors()
        curses.init_pair(ALERT_NONE, curses.COLOR_WHITE, -1)
        curses.init_pair(ALERT_PRINT, curses.COLOR_RED, -1)
        curses.init_pair(ALERT_CLEAR, curses.COLOR_GREEN, -1)

        # Color codes for showing HTTP status codes
        curses.init_pair(4, curses.COLOR_GREEN, -1)
        curses.init_pair(5, curses.COLOR_YELLOW, -1)
        curses.init_pair(6, curses.COLOR_CYAN, -1)
        curses.init_pair(7, curses.COLOR_RED, -1)

        # For keeping track of alerts
        alerted = Counter()
        alerted_uris = Counter()

        # By default show the top sites
        display = ord('h')

        while not self.check_exit():
            # Get the summary
            summary = self.collector.get_summary()
            time = summary.interval
            tstr = []

            if time.days:
                tstr += ['%d day%s' % (time.days, 's' if time.days > 1 else '')]

            hours, seconds = divmod(time.seconds, 3600)
            minutes, seconds = divmod(seconds, 60)

            if hours:
                tstr += ['%d hour%s' % (hours, 's' if hours > 1 else '')]
            if minutes:
                tstr += ['%d minute%s' % (minutes, 's' if minutes > 1 else '')]
            if seconds:
                tstr += ['%d second%s' % (seconds, 's' if seconds > 1 else '')]

            # Clear the screen
            stdscr.clear()

            # Print the title
            title = 'Statistics for the last %s' % (' '.join(tstr))
            stdscr.addstr(0, 0, title, curses.A_BOLD)
            stdscr.addstr(1, 0, 'Total: ')

            sequence = []
            messages = []
            for key, msg in [('hits', 'hits'), ('size', 'bytes transferred')]:
                value = getattr(summary, key)
                sequence.append((key, value))
                messages.append(msg)

            iterator = self._get_print(sequence, alerted, prefix='total')
            alert_msgs = []

            for (key, value, attr), msg in zip(iterator, messages):
                stdscr.addstr('%d %s ' % (value, msg), curses.color_pair(attr))

                if attr == ALERT_PRINT:
                    alert_msgs.append(('Alert for %s' % msg, attr))
                elif attr == ALERT_CLEAR:
                    alert_msgs.append(('Alert cleared for %s' % msg, attr))

            # Print the alert messages
            for ypos, (alertstr, attr) in zip(xrange(20, 22), alert_msgs):
                stdscr.addstr(ypos, 0, alertstr, curses.color_pair(attr))

            # Print the status messages
            fields = self.collector.get_top('status', 5)
            stdscr.addstr(2, 0, 'Top Status Codes: ')

            for status, count in fields:
                # Get an appropriate colour for the status message
                color = (int(status) / 100) + 2
                stdscr.addstr('%s(%d) ' % (status, count),
                              curses.color_pair(color))

            # Print the HTTP methods
            fields = self.collector.get_top('method', 5)
            stdscr.addstr(3, 0, 'Methods: ')

            for method, count in fields:
                stdscr.addstr('%s(%d) ' % (method, count))

            # Display the requested information
            if display == ord('h'):
                # Display the top Hits
                fields = self.collector.get_top('hits', self.top_count)
                title, fmt = FORMAT_INFO['hits']

                stdscr.addstr(4, 0, title.ljust(79), curses.A_REVERSE)

                uris = self._get_print(fields, alerted_uris, alt_key='hits')

                ypos = 5
                for uri, hits, attr in uris:
                    size = self.collector.get_uri_data(uri, 'size')
                    uri_str = fmt % (uri, hits, size)
                    stdscr.addstr(ypos, 0, uri_str, curses.color_pair(attr))
                    ypos += 1
                
            elif display == ord('b'):
                # Display the top uris by bytes transferred
                fields = self.collector.get_top('size', self.top_count)
                title, fmt = FORMAT_INFO['size']

                stdscr.addstr(4, 0, title.ljust(79), curses.A_REVERSE)

                uris = self._get_print(fields, alerted_uris, alt_key='size')

                ypos = 5
                for uri, size, attr in uris:
                    hits = self.collector.get_uri_data(uri, 'hits')
                    uri_str = fmt % (uri, size, hits)
                    stdscr.addstr(ypos, 0, uri_str, curses.color_pair(attr))
                    ypos += 1

            elif display == ord('r'):
                # Display the top referrers
                fields = self.collector.get_top('referer', self.top_count)
                title, fmt = FORMAT_INFO['referer']

                stdscr.addstr(4, 0, title.ljust(79), curses.A_REVERSE)

                ypos = 5
                for ref, hits in fields:
                    ref_str = fmt % (ref, hits)
                    stdscr.addstr(ypos, 0, ref_str)
                    ypos += 1

            elif display == ord('u'):
                # Display the top users
                fields = self.collector.get_top('user', self.top_count)
                title, fmt = FORMAT_INFO['user']

                stdscr.addstr(4, 0, title.ljust(79), curses.A_REVERSE)

                ypos = 5
                for user, hits in fields:
                    user_str = fmt % (user, hits)
                    stdscr.addstr(ypos, 0, user_str)
                    ypos += 1

            stdscr.addstr(22, 0, HELP_STR, curses.A_REVERSE)

            # Now that data is written to console, refresh it
            stdscr.refresh()

            # Wait for a key from a user or for a timeout to refresh
            key = stdscr.getch()

            # If the user does not enter data or hits ' ', refresh the screen
            if key in [curses.ERR, ord(' ')]:
                pass

            elif key in [ord('h'), ord('b'), ord('r'), ord('u')]:
                # Check if the key has changed
                if display != key:
                    alerted_uris = Counter()
                    display = key

            elif key == ord('q'):
                # Quit the application
                break
            else:
                pass

    def _get_print(self, sequence, alerted, alt_key=None, prefix=None):
        '''
        Get the information for printing data from a sequence.
        This api keeps track of alerts and the colors used to print them
        '''

        keys = []

        for alert, value in sequence:
            keys.append(alert)
            attr = ALERT_NONE

            if prefix:
                key = prefix + '_' + alert
            else:
                key = alt_key

            if key in self.alerts:
                alert_value = self.alerts[key]

                if value >= alert_value:
                    alerted[alert] = 1
                    attr = ALERT_PRINT
                else:
                    attr = ALERT_CLEAR if alerted.pop(alert, None) else attr

            yield (alert, value, attr)

        # Cleanup any alerts that are not visible anymore
        for key in alerted.keys():
            if key not in keys:
                alerted.pop(key)
