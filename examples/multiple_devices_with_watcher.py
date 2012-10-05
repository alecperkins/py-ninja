"""
An example showing how to use the Watcher to track multiple devices in one
process.
"""

from ninja.api      import NinjaAPI, Watcher
from ninja.devices  import TemperatureSensor, HumiditySensor

from datetime       import datetime



# Set up the NinjaAPI and Device wrappers:

# Access token from https://a.ninja.is/you#apiTab
api         = NinjaAPI('<YOUR_ACCESS_TOKEN>')

# Device GUID can be found using https://api.ninja.is/rest/v0/devices/?access_token=<YOUR_ACCESS_TOKEN>
device1     = TemperatureSensor(api, '<DEVICE_1_GUID>')
device2     = HumiditySensor(api, '<DEVICE_2_GUID>')

# The watcher will provide a single loop for polling all of the devices.
watcher     = Watcher(device1, device2)


# Output the temperature to stdio.
def printTempCelsius(inst, temperature):
    date = inst.last_read.isoformat()
    print '{date} - {id}: {temperature} C'.format(
        date=date,
        id=inst.guid,
        temperature=temperature.c,
    )

def printRelHumidity(inst, humidity):
    date = inst.last_read.isoformat()
    print '{date} - {id}: {humidity}%'.format(
        date=date,
        id=inst.guid,
        humidity=humidity,
    )


# Bind the output to the heartbeat event.
device1.onHeartbeat(printTempCelsius)
device2.onHeartbeat(printRelHumidity)

# Watch both devices in the same loop, triggering their heartbeats ever
# 10 seconds.
watcher.start(period=10)
