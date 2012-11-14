"""
An example showing how to use *Nodes* and the *Ticker* to manage a more
complicated flow of data. This example logs both the temperature and the
orientation to a CSV file. It also changes the color of the onboard LED
depending on the orientation of the block reported by the accelerometer.

A *Ticker* is used to generate tick cycles, and an *And* node is used to join
the temperature and orientation readings together for output to a *CSVWriter*
node.

The graph looks like this:

          +---------------------------------------------------+
          | [1] AccelerometerNode         [2] TemperatureNode |
          |            O                             O        | These are added
          |            +                             +        | to a Ticker to
          |            |                             |        | manage the ticks
          +------------|-----------------------------|--------+
                       |                             |
                       +---+------------------+      |
                           |              [D] |      | [E]
                       [A] |                  +->I<--+
                           v                [6] And
                           I                     O
                    [3] Channel                  +------------------+
                           O (w/transform)       |                  | [G]
          +----------------+                     | [F]              |
          |                |                     |                  v
      [C] |            [B] |                     v                  I
          v                |                     I                Echo [8]
          I                v              [7] Channel
    [5] Echo               I                     O (w/transform)
                    [4] LEDNode                  +
                                                 |
                                                 | [H]
                                                 |
                                                 v
                                                 I
                                         [9] CSVWriter

Don't worry, it's not as crazy as it looks. Not including the transform
functions, it's barely more than a dozen lines of code.
"""

from _examples import *

from datetime       import datetime

# Note that the Devices and Watcher are not imported, only Nodes and Ticker.
# The Nodes are wrappers around the lower-level devices, and the Ticker is
# a wrapper around the Watcher that adapts it to Nodes.
from ninja.api      import NinjaAPI
from ninja.nodes    import (
    AccelerometerNode,
    And,
    Channel,
    CSVWriter,
    Echo,
    LEDNode,
    TemperatureNode,
    Ticker
)



api = NinjaAPI(secrets.ACCESS_TOKEN)



"""
Create the nodes to be used:
"""

# Create the accelerometer node.
#    [1]
accel_node = AccelerometerNode(api=api, guid=secrets.ACCEL_ID)

# Create the temperature node.
#   [2]
temp_node = TemperatureNode(api=api, guid=secrets.TEMP_ID)

# Create the LED node to send the colors to.
#   [4]
led_node = LEDNode(api=api, guid=secrets.LED_ID)



# Create a transform channel to convert the raw orientation
# ('-12,-186,-167') to a color 'RRGGBB'. (The LED can only do 0 or 255
# on each color channel.)
#  [3]
channel = Channel()
def toRGB(in_data):
    print in_data
    data = []
    for d in in_data.get('data').split(','):
        d = abs(int(d))
        if d > 127:
            d = 255
        else:
            d = 0
        d = hex(d).split('x')[1].upper()
        if len(d) < 2:
            d = '0' + d
        data.append(d)
    return ''.join(data)
channel.setTransform(toRGB)

# Create a CSVWriter node that will log the temperature and orientation
# readings to the file `temp_and_accel_log.csv`.
#        [9]
temp_and_accel_logger = CSVWriter(
    file='temp_and_accel_log.csv',
    headers=['Date','Temperature (K)','Orientation (X,Y,Z)'],
)

# Create a Channel that structures the data in a way suitable for the CSVWriter.
#      [7]
csv_prep_channel = Channel()
def prepLogRow(in_data):
    date = in_data[temp_node.id]['last_read']
    temp = in_data[temp_node.id]['data']
    accel = in_data[accel_node.id]['data']
    return [date.isoformat(), temp.k, accel]
csv_prep_channel.setTransform(prepLogRow)



"""
Connect the nodes to build the graph.
"""

# Connect the transform channel to the accel output...
#     [A]
channel.i.connect(accel_node.o)

# ...and to the LED node (and an Echo to print the rgb value).
#     [B,C]         [5]
channel.o.connect(Echo('RGB').i, led_node.i)

# Create an And node to join the temperature and orientation data together.
#   [6]
and_node = And()
#       [D,E]
and_node.i.connect(temp_node.o, accel_node.o)

# Attach the And to the channel that formats the CSV data (and an Echo).
#       [F,G]                              [8]
and_node.o.connect(csv_prep_channel.i, Echo('And').i)

# Connect the formatter channel to the CSVWriter node to save the data to file.
#        [H]
csv_prep_channel.o.connect(temp_and_accel_logger.i)



"""
Set up the Ticker and start the tick cycles that feed data into the graph.
"""

# Pre- and post-tick prints to show the beginning and end of the tick cycle.
def printPre(ticker):
    print '\npre-tick', ticker.counter + 1
def printPost(ticker):
    print 'post-tick', ticker.counter, '\n'

ticker = Ticker(temp_node, accel_node, post_tick=printPost)
ticker.addPreTick(printPre) # alternate way to add pre-/post-tick functions.
ticker.start()

