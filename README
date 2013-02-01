# Omphalos - A set of libraries for collecting logs

Omphalos is a set of components that can be used for collecting logs from
a distributed set of servers. Broadly, the components are defined as follows

```
 Source   +---------+    +--------+    +-----------+     +-----------+    +--------+
 -------->| Monitor |--->| Parser |--->| Transport |---->| Collector |--->| Output |
          +---------+    +--------+    +-----------+     +-----------+    +--------+
```

Each component is defined as a plugin

## Monitor
Plugins for monitoring log sources.

Current plugins provide for using INotify (Linux) or Poll mechanisms to tail files.

TODO: Try using python watchdog for providing a platform independent mechanism for
monitoring files

## Parser
Each line obtained by the monitor plugin is passed to a parser which converts it to
a common data format.

Current plugins are for tailing and parsing CLF and W3C formatted logs

## Transport
Transport plugins take care of sending the data to the collector, which could be
local or remote.

Currently, a dummy plugin is provided which just appends the data to a local collector

TODO: Implement transport plugins using ZeroMQ, UDP, AMQP etc. (kombu?)

## Collector
Collector plugins collect and store the data. They also provide APIs for querying
the data

Current plugins implemented
* An aggregator plugin which simply keeps a summary of the data
* A sliding window plugin which keeps data for a pre-defined period
* A skeletal ElasticSearch plugin which can be used for storing data in ElasticSearch

TODO Plugins
* An HBase or OpenTSDB plugin

## Output
Output plugins are used for displaying the data from the collectors

Current plugins implemented
* A console plugin which uses ncurses to display the data in the console. This also supports displaying alerts and clearing them (for individual URIs or for the entire site)

TODO plugins
* A REST API
* A web UI using Django and D3.js

## Usage
The library can be used by chaining different plugins together

A sample daemon is provided which can be used for showcasing how the interfaces can be used

```
$ python ldaemon.py /path/to/access.log
```

