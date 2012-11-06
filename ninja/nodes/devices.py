from .core  import Node, HasInput, HasOutput
from ninja.devices  import RGBLED, Accelerometer, TemperatureSensor


class DeviceNode(Node):    

    def __init__(self, api=None, guid=None, *args, **kwargs):
        super(DeviceNode, self).__init__(*args, **kwargs)
        self.device = self.device_class(api, guid)

        if self.hasOutput():
            def cb(*args):
                self.emitData()
            self.device.onHeartbeat(cb)

    @property
    def device_class(self):
        raise NotImplementedError('')

    def emitData(self):
        if self.hasOutput():
            d = self.device
            self.o.emit({
                'guid'      : self.device.guid,
                'last_read' : self.device.last_read,
                'data'      : self.device.data,
            })
            





class LEDNode(DeviceNode, HasInput):
    device_class = RGBLED
    def receiveData(self, data, from_id):
        self.device.setColor(data)



class AccelerometerNode(DeviceNode, HasOutput):
    device_class = Accelerometer

    def emitData(self):
        super(AccelerometerNode, self).emitData()


class TemperatureNode(DeviceNode, HasOutput):
    device_class = TemperatureSensor
