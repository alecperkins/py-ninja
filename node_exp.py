"""
Experimenting with the syntax and functionality of connecting nodes.

Every node MUST have an Input and/or Output. Inputs MUST be connected to
Outputs, and Outputs MUST be connected to Inputs. Each connector MAY be
connected to one or more of the opposite type of connector.

Nodes:

* Devices (& simulated devices)
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


# channel.o.connect(echo)
# latest_data = channel.o()
# channel.i(new_data)





from ninja.nodes import Echo, Counter, Channel, Source, CSVWriter, JSONWriter, If, Buffer, Sink, HTTPReader


print "\n\n\t**\tConnect input to input (fails)"
channel = Channel()
echo = Echo()
try:
    channel.i.connect(echo.i)
except Exception as e:
    print e

print "\n\n\t**\tConnect output to output (fails)"
channel = Channel()
counter = Counter()
try:
    channel.o.connect(counter.o)
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



print "\n\n\t**\tConnect a source node"
channel = Channel()
source = Source('some data')
source.o.connect(channel.i)
channel.o.connect(*[Echo().i for x in range(10)])
for i in range(10):
    source.emitData()


print "\n\n\t**\tConnect a sink node"
counter = Counter()
def printData(data):
    print 'sink received', data
sink = Sink(on_receive=printData)
counter.o.connect(sink.i)
counter.startCounter()




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


print "\n\n\t**\tRead & Write"
channel = Channel()
counter = Counter()
counter.startCounter(5, delay=0.1)
channel.o.connect(*[Echo().i for x in range(10)])
print 'Last read:', counter.o()
print 'Write: "SOME DATA"'
channel.i('SOME DATA')


import random
print "\n\n\t**\tWrite to csv file"
counter = Counter()
counter.o.connect(Echo().i)
csvnode = CSVWriter(file='x.csv', headers=['a','b','c','d'])
counter.o.connect(csvnode.i)
counter.startCounter(data=lambda x: [x*random.random(),x+1*random.random(),x+2*random.random(),x+3*random.random()])



print "\n\n\t**\tWrite to json file"
counter = Counter()
counter.o.connect(Echo().i)
jsonnode = JSONWriter()
counter.o.connect(jsonnode.i)
counter.startCounter(data=lambda x: { 'file': str(x) + '.json', 'data': { 'a': [x*random.random(),x+1*random.random(),x+2*random.random(),x+3*random.random()] } })



print "\n\n\t**\tIf"
counter = Counter()
def do_test(data):
    return data % 2 == 0
if_node = If(test=lambda x: x % 2 == 0)
if_node.o.connect(Echo().i)
if_node.fail.connect(Echo('Fail', message='x % 2').i)
counter.o.connect(Echo().i, if_node.i)
counter.startCounter()



print "\n\n\t**\tUse a buffer"
buffer_node = Buffer()
buffer_node.o.connect(Echo(message='buffered').i)
counter = Counter()
counter.o.connect(buffer_node.i)
counter.o.connect(Echo().i)
counter.startCounter(10, delay=0.3)
buffer_node.flush()



print "\n\n\t**\tSet a flush_at threshold on the buffer"
buffer_node = Buffer(flush_at=5)
buffer_node.o.connect(Echo(message='buffered').i)
counter = Counter()
counter.o.connect(buffer_node.i)
counter.o.connect(Echo().i)
counter.startCounter(15, delay=0.3)
buffer_node.flush()


print "\n\n\t**\tSet a keep limit on the buffer"
buffer_node = Buffer(keep=5)
buffer_node.o.connect(Echo(message='buffered').i)
counter = Counter()
counter.o.connect(buffer_node.i)
counter.o.connect(Echo().i)
counter.startCounter(10, delay=1)
buffer_node.flush()




import json
print "\n\n\t**\tHTTPReader"
get = HTTPReader(url='http://openweathermap.org/data/station/2121?type=json')
channel = Channel()
channel.setTransform(lambda x: json.loads(x))
channel.o.connect(Echo().i)
get.o.connect(Echo().i, channel.i)
get.emitData()


