import sys
import threading
import time

from monitor.inotify import MonitorINotify
from monitor.poll import Poll
from collector.slider import Slider
from output.console import Console
from parser.clf import CLFParser
from transport.dummy import Dummy

# Start the sliding collector with 10 minutes of storage
conf = {}
collector = Slider(conf, 60)

# Start a dummy transport
transport = Dummy(collector=collector)

# Start the parser
parser = CLFParser(sys.argv[1])

# Start the console display
conf = {
    'refresh_time' : 10,
    'top_count': 15,
    'alerts': {
        'total_size': 1024,
        'total_hits': 10,
        'size': 512,
        'hits': 5,
    },
}

display = Console(conf, collector)

# Start the monitor
conf = {
    'file_path': sys.argv[1]
}

monitor = MonitorINotify(conf, transport, parser)
#monitor = Poll(conf, transport, parser)

# Start two threads. One for monitoring and one for displaying
# on the console
try:
    monitor_th = threading.Thread(target=monitor.run)
    display_th = threading.Thread(target=display.run)
    monitor_th.daemon = True
except Exception:
    print('Error in running app')
    sys.exit(-1)

monitor_th.start()
display_th.start()
