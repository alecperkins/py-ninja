"""
A basic example of printing the status of a button.
"""

from _examples import *

from ninja.api      import NinjaAPI
from ninja.devices  import Button



api         = NinjaAPI(secrets.ACCESS_TOKEN)
button      = Button(api, secrets.BUTTON_ID)



def printStatus(inst, data):
    if inst.isPushed():
        print inst.last_read, ': button is pushed'
    else:
        print inst.last_read, ': button is not pushed'

button.onHeartbeat(printStatus)



# Poll the button's status in 5 second intervals.
button.pulse(period=5)
