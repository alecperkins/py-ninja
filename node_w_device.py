"""
This script set the Block's LED based on its orientation, using a Channel to
transform the orientation data incoming from the Accelerometer node and send it
to the LED node. The graph also includes Echo nodes for monitoring the values
in the terminal.
"""

from ninja.api      import NinjaAPI
from ninja.devices  import Accelerometer, RGBLED
from ninja.nodes    import Channel, Echo, LEDNode, AccelerometerNode

from datetime       import datetime

import secrets

# Initialize the API wrapper with the access token.
api = NinjaAPI(secrets.ACCESS_TOKEN)



# Create the actual graph, which looks like this:
#
# (1) Accelerometer    (2) Echo
#           O ------------> I
#                   (B)
#           | (A)
#           |
#           V
#     
#           I
#    (3) Channel ('RR,GG,BB' -> flattened 'RRGGBB')
#           O
#     
#           |    (5) Echo
#           |-------> I
#           |   (D)
#           |
#           | (C)
#           V
#     
#           I
#     (4) LEDNode

# Create the accelerometer node.
#    (1)
accel_node = AccelerometerNode(api=api, guid=secrets.ACCEL_ID)

# Connect an echo to the accelerometer node to output the raw data
#    (B)              (2)
accel_node.o.connect(Echo().i)

# Create a transform channel to convert the raw orientation
# ('-12,-186,-167') to a color 'RRGGBB'. (The LED can only do 0 or 255
# on each color channel.)
#  (3)
channel = Channel()
def toRGB(in_data):
    data = []
    for d in in_data[1].split(','):
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

# Create the LED node to send the colors to.
#   (4)
led_node = LEDNode(api=api, guid=secrets.LED_ID)

# Connect the transform channel to the accel output...
#     (A)
channel.i.connect(accel_node.o)

# ...and to the LED node (and an echo to print the rgb value).
#     (C,D)         (5)
channel.o.connect(Echo('RGB').i, led_node.i)


"""
TODO: How to handle this better?
"""
# Start the pulsing of the device.
accel_node.device.pulse(period=1)



