'''
A collector which keeps data only for a specified set of time (in memory).

WARNING:
This class aggregates data in memory. For large number of unique URL's,
it is advised to use a different plugin based on a time-series database.
'''

import threading
from datetime import datetime, timedelta
from collections import deque

from collector.aggregate import Aggregate


class Slider(Aggregate):
    '''A collector which keeps data only for a specified set of time'''

    def __init__(self, conf, timeout):
        # Maintain a queue for storing the datasets in order of their arrival
        # Decks (deque) are good for adding and popping data at both ends
        # with good performance (O(1)) compared to lists. Decks are also
        # thread-safe and memory efficient
        self.timeseries = deque()
        self.timeout = timedelta(seconds=timeout)

        # The overall aggregation info is maintained separately
        super(Slider, self).__init__(conf, timeout)

        # This is a dirty little hack to cleanup the old data if no
        # new data is being added. In a truly distributed mode, this
        # can be done via other timeout mechanisms
        self.lock = threading.Lock()

    def _cleanup(self):
        '''
        Cleanup any old data that is there in the queue
        '''

        # Calculate the reference time
        ref_time = datetime.now() - self.timeout

        with self.lock:
            while self.timeseries:
                old = self.timeseries[0]
                if old.timestamp >= ref_time:
                    break

                old = self.timeseries.popleft()
                super(Slider, self).remove_data(old)

    def add_data(self, data):
        '''
        Add data to the collector. This keeps the new data in a queue
        but also cleans-up any pending data

        @param data: The data that is being collected
        @type data: L{Data}
        '''

        # Cleanup old entries from the data list. This can be time
        # consuming. We can look at scheduling this separately when our
        # traffic loads are volumnious
        self._cleanup()

        if data.timestamp < self.started_at:
            return

        self.timeseries.append(data)
        super(Slider, self).add_data(data)

    def get_summary(self):
        '''
        Get a summary of the collected data

        @return: The summary of the data
        @rtype: L{Summary}
        '''
        self._cleanup()
        return super(Slider, self).get_summary()

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
        self._cleanup()
        return super(Slider, self).get_top(dtype, count)
