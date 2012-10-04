"""
An example showing how to use the Watcher to track multiple devices in one
process.
"""

from ninja.api      import NinjaAPI, Watcher
from ninja.devices  import TemperatureSensor

from datetime       import datetime



# Set up the NinjaAPI and Device wrappers:

# Access token from https://a.ninja.is/you#apiTab
api         = NinjaAPI('<YOUR_ACCESS_TOKEN>')

# Device GUID can be found using https://api.ninja.is/rest/v0/devices/?access_token=<YOUR_ACCESS_TOKEN>
device1     = TemperatureSensor(api, '<DEVICE_1_GUID>')
device2     = TemperatureSensor(api, '<DEVICE_2_GUID>')

# The watcher will provide a single loop for polling all of the devices.
watcher     = Watcher()


# Output the temperature to stdio.
def printTempCelsius(inst, data):
    date = inst.last_read.isoformat()
    print date + ' - ' + inst.guid + str(data.c)

# Bind the output to the heartbeat event.
device1.onHeartbeat(printTempCelsius)
device2.onHeartbeat(printTempCelsius)

# Watch both devices in the same loop, triggering their heartbeats ever
# 10 seconds.
watcher.watch(device1)
watcher.watch(device2)
watcher.start(period=10)
