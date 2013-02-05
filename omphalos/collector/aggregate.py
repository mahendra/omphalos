'''
An aggregating collector which keeps updating data into a record set
This collector is also used as a base class for other collectors
'''

from collections import Counter, defaultdict
from datetime import datetime, timedelta

from collector.base import Collector
from collector.base import Summary


class Aggregate(Collector):
    '''An in memory aggregating collector implementation'''
    def __init__(self, conf, timeout):
        self.data = defaultdict(Counter)
        self.started_at = datetime.now() - timedelta(seconds=1)
        self.created_at = self.started_at
        self.updated_at = datetime.now()
        self.total = Counter({'hits': 0, 'size': 0})

    def add_data(self, data):
        '''
        Add data to the collector

        @param data: The data that is being collected
        @type data: L{Data}
        '''
        size = int(data.size)
        self.total.update({'hits': 1, 'size': size})

        self.data['hits'].update({data.uri: 1})
        self.data['size'].update({data.uri: size})
        self.data['status'].update({data.status: 1})
        self.data['method'].update({data.method: 1})

        if data.referer:
            self.data['referer'].update({data.referer: 1})

        if data.user:
            self.data['user'].update({data.user: 1})

        # Remove items with 0 value
        for key in self.data:
            self.data[key] += Counter()

        self.updated_at = datetime.now()

    def remove_data(self, data):
        '''
        Remove data of a log line from the collected information.
        Used when data is being purged.

        @param data: The data that is being collected
        @type data: L{Data}
        '''

        size = int(data.size)
        self.total.subtract({'hits': 1, 'size': size})

        self.data['hits'].subtract({data.uri: 1})
        self.data['size'].subtract({data.uri: size})
        self.data['status'].subtract({data.status: 1})
        self.data['method'].subtract({data.method: 1})

        if data.referer:
            self.data['referer'].subtract({data.referer: 1})

        if data.user:
            self.data['user'].subtract({data.user: 1})

        # Remove items with 0 value
        for key in self.data:
            self.data[key] += Counter()

        self.started_at = data.timestamp
        self.updated_at = datetime.now()

    def get_summary(self):
        '''
        Get a summary of the collected data

        @return: The summary of the data
        @rtype: L{Summary}
        '''
        interval = datetime.now() - self.started_at
        return Summary(interval=interval, **self.total)

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
        return self.data[dtype].most_common(count)

    def get_uri_data(self, uri, dtype):
        '''
        Get the specified data for the uri

        @param uri: The URI for which data is requested
        @type uri: C{str}

        @param dtype: Must be 'hits', 'size'
        @type dtype: C{str}

        @return: The requested count
        @rtype: C{int}
        '''
        return self.data[dtype][uri]

    def reset_interval(self, start_at):
        '''
        Reset the interval by adjusting the start time
        '''

        if start_at > self.created_at:
            self.started_at = start_at
