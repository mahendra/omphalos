'''
A collector which uses Elasticsearch as a time-series DB
'''

import pyes
import simplejson

from collector.base import Collector


class ElasticSearch(Collector):
    def __init__(self, conf, timeout):
        """Sync the data to elastic search"""

        self.timeout = timeout

        # Initiate the ES connection from the configuration
        self.es = pyes.ES()

        # Do the following here
        # 1) Create required indices in ES
        #    self.es.create_index(conf['es_index'])
        # 2) Update mappings for ES
        #    self.es.put_mapping()

    def add_data(self, data):
        '''
        Add data to ElasticSearch

        @param data: The data that is being collected
        @type data: L{Data}
        '''
        # Make a JSON of the data and index it to ES with a time to live
        esdata = simplejson.dumps(data)
        self.es.index(ttl=self.timeout)

    def get_summary(self):
        # Run a query to ES for the summary and return the data
        # accordingly
        pass

    def get_top(self, dtype, count):
        # Run a query to ES for the summary and return the data
        # accordingly
        pass

    def get_uri_data(self, uri, dtype):
        # Run a query to ES for the summary and return the data
        # accordingly
        pass
