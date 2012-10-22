"""
Experimenting with the syntax and functionality of connecting nodes.

Every node MUST have an Input and/or Output. Inputs MUST be connected to
Outputs, and Outputs MUST be connected to Inputs. Each connector MAY be
connected to one or more of the opposite type of connector.

Nodes:

* Devices
* Logic
* Virtual devices (eg HTTP, ZMQ)
* Data storage (file, csv, SQL, Mongo, Redis)
* Channel (pass-through/aggregator node)



Qs:

* How do the data storage nodes know the schema?
    - They're just simple wrappers around the storage system, The data needs to
      be translated first.

* Should outputs have a `read` method, so the data can be pull instead of push?

* Data is not copied, so can be a reference. Should it always be a copy?



Thoughts:

* Parsers for handling incoming HTTP requests, ie callbacks
  - leave the actual URL routing/handling to app

* `connect(*args)` batch method that creates a channel and plugs in all the
  specified inputs and outputs, returning the channle

* Graph visualizer
"""


from ninja.nodes import Echo, Counter, Channel, Static


print "\n\n\t**\tConnect input to input (fails)"
channel = Channel()
echo = Echo()
try:
    channel.i.connect(echo.i)
except Exception as e:
    print e



print "\n\n\t**\tConnect input to output"
counter = Counter()
echo = Echo()
counter.o.connect(echo.i)
counter.startCounter(2)



print "\n\n\t**\tConnect output to input"
counter = Counter()
echo = Echo()
echo.i.connect(counter.o)
counter.startCounter(2)



print "\n\n\t**\tConnect multiple nodes to one"
counter = Counter()
counter.o.connect(*[Echo().i for x in range(10)])
counter.startCounter(2, delay=2)



print "\n\n\t**\tConnect with a channel"
channel = Channel()
counter = Counter()
counter.o.connect(channel.i)
channel.o.connect(*[Echo().i for x in range(10)])
counter.startCounter(10, delay=0.1)



print "\n\n\t**\tConnect a static node"
channel = Channel()
static = Static('some data')
static.o.connect(channel.i)
channel.o.connect(*[Echo().i for x in range(10)])
for i in range(10):
    static.emitData()



print "\n\n\t**\tSet the counter data to a dictionary"
channel = Channel()
counter = Counter()
counter.o.connect(channel.i)
channel.o.connect(*[Echo().i for x in range(10)])
counter.startCounter(10, delay=0.1, data={'a': 1})



print "\n\n\t**\tSet the counter data to a callable"
channel = Channel()
counter = Counter()
counter.o.connect(channel.i)
channel.o.connect(*[Echo().i for x in range(10)])
counter.startCounter(10, delay=0.1, data=lambda x: x * 100)



print "\n\n\t**\tMake the channel a transform, eg to set up a schema for a storage node"
channel = Channel()
channel.setTransform(lambda x: { 'file': '%s.txt' % (x,), 'data': x })
counter = Counter()
counter.o.connect(channel.i)
channel.o.connect(*[Echo().i for x in range(10)])
counter.startCounter(10, delay=0.1)


