'''
The data structures required for the tool to work
'''

from collections import namedtuple

# The structure in which data has to be added to the collector plugins
# We shall use a namedtuple because it can easily be accessed like
# an object, a dict or a tuple. Also, it is easily serialisable.
# On top of it, it is memory efficient (as per Guido)
Data = namedtuple('Data', ('uri', 'timestamp', 'size', 'status',
                           'method', 'referer', 'user'))
