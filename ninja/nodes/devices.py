from .core  import Node, HasInput, HasOutput
from ninja.devices  import RGBLED, Accelerometer



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



class LEDNode(DeviceNode, HasInput):
    device_class = RGBLED
    def receiveData(self, data):
        self.device.setColor(data)



class AccelerometerNode(DeviceNode, HasOutput):
    device_class = Accelerometer
    def emitData(self):
        self.o.emit((self.device.last_read, self.device.data))


