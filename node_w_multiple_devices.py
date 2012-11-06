
from ninja.api      import NinjaAPI, Watcher
from ninja.devices  import Accelerometer, RGBLED
from ninja.nodes    import Channel, Echo, LEDNode, AccelerometerNode, TemperatureNode
from ninja.nodes import And, Ticker
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

# Create a transform channel to convert the raw orientation
# ('-12,-186,-167') to a color 'RRGGBB'. (The LED can only do 0 or 255
# on each color channel.)
#  (3)
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

# Create the LED node to send the colors to.
#   (4)
led_node = LEDNode(api=api, guid=secrets.LED_ID)

# Connect the transform channel to the accel output...
#     (A)
channel.i.connect(accel_node.o)

# ...and to the LED node (and an echo to print the rgb value).
#     (C,D)         (5)
# channel.o.connect(Echo('RGB').i, led_node.i)



temp_node = TemperatureNode(api=api, guid='1012BB013214_0_0_1')
# temp_node.o.connect(Echo().i)


channel2 = Channel()
channel2.i.connect(temp_node.o, accel_node.o)
# channel2.o.connect(Echo('BOTH').i)

and_node = And()
and_node.i.connect(temp_node.o, accel_node.o)
and_node.o.connect(Echo('And').i)

ticker = Ticker(temp_node, accel_node)
ticker.start()

