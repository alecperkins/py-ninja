"""
Set the Block's LED based on its orientation, using a Channel to
transform the orientation data incoming from the Accelerometer node and
send it to the LED node
"""


from ninja.api      import NinjaAPI
from ninja.devices  import Accelerometer, RGBLED

from datetime       import datetime

import secrets

api         = NinjaAPI(secrets.ACCESS_TOKEN)
accel       = Accelerometer(api, secrets.ACCEL_ID)
led         = RGBLED(api, secrets.LED_ID)


from ninja.nodes import Emit, Channel, Echo, Node, HasInput

# Wrap the accelerometer in an emit node (until devices are nodes)
def x():
    if accel.last_read:
        d = accel.last_read.isoformat()
    else:
        d = ''
    return (d, accel.data)
s = Emit(x)

# Connect an echo to the accelerometer node to output the raw data
s.o.connect(Echo().i)



# Create a transform channel to convert the raw orientation
# ('-12,-186,-167') to a color 'RRGGBB'. (The LED can only do 0 or 255
# on each color channel.)
c = Channel()
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
c.setTransform(toRGB)

# Wrap the LED in a Node
class LEDNode(Node, HasInput):
    def receiveData(self, data):
        led.setColor(data)
lnode = LEDNode()

# Connect the transform channel to the accel output, and to the LED node (and
# an echo to print the rgb value)
c.i.connect(s.o)
c.o.connect(Echo('RGB').i, lnode.i)

# Wrap the node emitter in a callback for the heartbeat
def emitD(*args):
    s.emitData()
accel.onHeartbeat(emitD)


accel.pulse(period=1)



