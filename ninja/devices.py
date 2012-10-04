import copy, time
from datetime import datetime

from .units import Temperature

class Events(object):
    def __init__(self):
        self._callbacks = {}

    # Bind to events
    def on(self, event, callback):
        if not event in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
        return self

    def off(self, event):
        self._callbacks[event] = []
        return self

    def _fire(self, event, *args, **kwargs):
        callbacks = self._callbacks.get(event, [])
        for callback in callbacks:
            callback(self, *args, **kwargs)



class Device(Events):
    """
    Base class for Devices.

        device.guid
        device.type
        device.name
        device.is_sensor
        device.is_actuator
        device.data
        device.last_heartbeat
        device.last_read


    """

    class Events(object):
        HEARTBEAT   = 'heartbeat'  # self, data
        CHANGE      = 'change'  # self, data, previous_data

    def __init__(self, api, guid, info={}):
        self._callbacks = {}

        self.api            = api
        self.guid           = guid
        self.type           = info.get('device_type', None)
        self.name           = info.get('shortName', None)
        self.is_sensor      = (info.get('is_sensor', None) == 1)
        self.is_actuator    = (info.get('is_actuator', None) == 1)
        self.data           = None
        self.last_heartbeat = None
        self.last_read      = None

    def heartbeat(self):
        data = self.api.updateDevice(self.guid)
        if data['id'] == 0:
            previous_data       = copy.deepcopy(self.data)
            self.last_heartbeat = datetime.utcnow()
            self.data           = self._parse(data['data']['DA'])
            last_read           = data['data']['timestamp']
            self.last_read      = datetime.utcfromtimestamp(last_read / 1000)

            self._fire(Device.Events.HEARTBEAT, self.data)
            if self.data != previous_data:
                self._fire(Device.Events.CHANGE, self.data, previous_data)

        return self.last_read, self.data

    def asDict(self, for_json=False):
        fields = (
            'guid',
            'type',
            'name',
            'is_sensor',
            'is_actuator',
            'data',
            'last_heartbeat',
            'last_read',
        )
        device_dict = {}
        for field in fields:
            device_dict[field] = getattr(self, field)

        if for_json:
            device_dict['data'] = self._dataToJSON(device_dict['data'])
        return device_dict

    # Shortcut for on('heartbeat', callback).
    def onHeartbeat(self, callback):
        return self.on(Device.Events.HEARTBEAT, callback)

    def pulse(self, period=10):
        while True:
            self.heartbeat()
            time.sleep(period)
        return

    # Parses the response data. Override this to handle specific sensor responses.
    # (Default is a pass-through.)
    def _parse(self, data):
        return data

    # Parser for converting data to JSON-friendly format.
    # (Default is a pass-through.)
    def _dataToJSON(self):
        return self.data



class TemperatureSensor(Device):
    def _parse(self, data):
        return Temperature(c=data)

    def _dataToJSON(self):
        return float(self.data)


