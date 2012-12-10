import copy, time
from datetime import datetime

from .events    import Events
from .units     import Temperature


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
        HEARTBEAT   = 'heartbeat'   # self, data
        CHANGE      = 'change'      # self, data, previous_data

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

    def __str__(self):
        return '{device_name} ({class_name})'.format(
            class_name=self.__class__.__name__,
            device_name=self.name,
        )

    def __repr__(self):
        return str(self)

    def heartbeat(self, silent=False):
        data = self.api.getDeviceHeartbeat(self.guid)
        if data['id'] == 0:
            previous_data       = copy.deepcopy(self.data)
            self.last_heartbeat = datetime.utcnow()
            self.data           = self._parse(data['data']['DA'])
            last_read           = data['data']['timestamp']
            self.last_read      = datetime.utcfromtimestamp(last_read / 1000)

            # Fire the events unless suppressed.
            if not silent:
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
            device_dict['data'] = self._dataToJSON()
            if self.last_read:
                device_dict['last_read'] = self.last_read.isoformat()
            if self.last_heartbeat:
                device_dict['last_heartbeat'] = self.last_heartbeat.isoformat()
        return device_dict

    # Shortcut for on('heartbeat', callback).
    def onHeartbeat(self, callback):
        return self.on(Device.Events.HEARTBEAT, callback)

    def pulse(self, period=10):
        while True:
            self.heartbeat()
            time.sleep(period)
        return

    def setWebhookURL(self, url):
        return self.api.setDeviceWebhookURL(self.guid, url)

    def getWebhookURL(self):
        return self.api.getDeviceWebhookURL(self.guid)

    def clearWebhookURL(self):
        return self.api.clearDeviceWebhookURL(self.guid)

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



class HumiditySensor(Device):
    pass



class LightSensor(Device):
    pass



class Accelerometer(Device):
    pass


class Button(Device):
    def isPushed(self):
        return self.data == 0



from units import Color
class RGBLED(Device):
    def __init__(self, *args, **kwargs):
        super(RGBLED, self).__init__(*args, **kwargs)
        self._last_color = Color.BLACK

    def setColor(self, *args):
        if not self._last_color:
            self._last_color = Color.WHITE

        color = Color(*args)
        data = {
            'DA': color.hex
        }
        self.api._makePUTRequest(self.api.getDeviceURL(self.guid), data)
        return

    def turnOn(self): # turns on to last color
        self.setColor(self._last_color)

    def turnOff(self):
        self._last_color = self.data
        self.setColor(Color.BLACK)


TYPE_MAP = {
    'button': Button,
    'rgbled': RGBLED,
    'orientation': Accelerometer,
    'temperature': TemperatureSensor,
    'humidity': HumiditySensor,
    'light': LightSensor,
}
