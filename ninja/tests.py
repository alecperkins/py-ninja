import json
import unittest

from datetime import datetime


class Mock_Response(object):

    def __init__(self, status_code=200, content=''):
        self.status_code = status_code
        self.content = content


DEVICES = {
    '1': {
        'css_class'     : 'sensor serial dht22 digital temp',
        'default_name'  : 'Temperature',
        'device_type'   : 'temperature',
        'did'           : '9',
        'gid'           : '2',
        'is_sensor'     : 1,
        'is_actuator'   : 0,
        'is_silent'     : 0,
        'meta'          : {},
        'shortName'     : 'Temperature',
        'subDevices'    : {},
        'vid'           : '0',
    },
}

HEARTBEATS = {
    '1': {
        'result'    : 1,
        'error'     : None,
        'id'        : 0,
        'data': {
            'G'     : '3',
            'V'     : 0,
            'D'     : 9,
            'DA'    : 24.2,
            'GUID'  : '1',
        }
    },
    '2': {
        'result'    : 1,
        'error'     : None,
        'id'        : 0,
        'data': {
            'G'     : '0',
            'V'     : 0,
            'D'     : 1000,
            'DA'    : '00FF00',
            'GUID'  : '2',
        }
    }
}

class Mock_NinjaAPI(object):

    def getDeviceHeartbeat(self, guid):
        content = HEARTBEATS[guid]
        content['data']['timestamp'] = int(datetime.now().strftime('%s')) * 1000 # because JavaScript
        return Mock_Response(content=json.dumps(content))

    # def get404(self, *args):



class Mock_Device(object):

    def __init__(self, *args, **kwargs):
        self.heartbeat_count = 0

    def heartbeat(self):
        self.heartbeat_count += 1
        return






class Test_Temperature(unittest.TestCase):

    def setUp(self):
        from .units import Temperature
        from decimal import Decimal
        self.Decimal = Decimal
        self.Temperature = Temperature

        self.temp100 = Temperature(100)

    def testUnits(self):
        self.assertEqual(self.temp100.k, self.Decimal('100'))
        self.assertEqual(self.temp100.c, self.Decimal('-173.15'))
        self.assertEqual(self.temp100.f, self.Decimal('-279.670'))
        self.assertEqual(self.temp100.r, self.Decimal('180.00'))

    def testOperators(self):
        self.temp100 += 100
        self.assertEqual(self.temp100.k, self.Decimal('200'))
        self.temp100 -= 100
        self.assertEqual(self.temp100.k, self.Decimal('100'))
        t = self.temp100 + 100
        self.assertEqual(t.k, self.Decimal('200'))
        t = self.temp100 - 100
        self.assertEqual(t.k, self.Decimal('0'))
        t = self.temp100 * 4
        self.assertEqual(t.k, self.Decimal('400'))
        t = self.temp100 / 4
        self.assertEqual(t.k, self.Decimal('25'))
        t = self.temp100 * self.Temperature(4)
        self.assertEqual(t.k, self.Decimal('400'))
        t = self.temp100 / self.Temperature(4)
        self.assertEqual(t.k, self.Decimal('25'))

    def testSubZero(self):
        self.assertRaises(ValueError, self.Temperature, -100)



# class Test_NinjaAPI(unittest.TestCase):
#     def setUp(self):
#         from .api import NinjaAPI
#         self.NinjaAPI = NinjaAPI

#     def testRequireAccessToken(self):
#         self.assertRaises(ValueError, self.NinjaAPI)
#         self.assertRaises(ValueError, self.NinjaAPI, 1, 2, 3)

class Test_Device(unittest.TestCase):
    def setUp(self):
        from .devices import Device
        self.Device = Device
        self.api = Mock_NinjaAPI()

    def testHeartbeat(self):
        guid = '1'
        d = self.Devices(self.api, guid)
        heartbeat_was_called = False
        def cb(inst, data):
            self.assertEqual(data, HEARTBEATS[guid])
            global heartbeat_was_called
            heartbeat_was_called = True
        # d.heartbeat()
        self.assertTrue(heartbeat_was_called)

