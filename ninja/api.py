import json
import requests
import time

from datetime   import datetime
from exceptions import Exception, ValueError



class NinjaAPIError(Exception):
    pass



class NinjaAPI(object):

    API_ROOT_URL    = 'https://api.ninja.is/rest/'
    STREAM_ROOT_URL = 'https://stream.ninja.is/rest/'
    API_VERSION     = 'v0/'

    USER_URL        = API_ROOT_URL + API_VERSION + 'user'
    DEVICES_URL     = API_ROOT_URL + API_VERSION + 'devices'
    DEVICE_ROOT_URL = API_ROOT_URL + API_VERSION + 'device'


    def __init__(self, *args):
        if len(args) != 1:
            raise ValueError('NinjaAPI instance requires an access token')
        
        self.access_token = args[0]


    def _makeGETRequest(self, url, binary=False):

        params = {
            'user_access_token': self.access_token,
        }

        res = requests.get(url, params=params)   

        if res.status_code == 200:
            if binary:
                content = res.content
            else:
                try:
                    content = json.loads(res.content)
                except ValueError:
                    raise NinjaAPIError("Did not get a JSON object (check device id)")
            return content
        else:
            raise NinjaAPIError('Got status code %s, expected 200' % (res.status_code,))

    def _makePUTRequest(self, url, data):
        params = {
            'user_access_token': self.access_token,
        }
        res = requests.put(url, params=params, data=data)   

        if res.status_code == 200:
            try:
                content = json.loads(res.content)
            except ValueError:
                raise NinjaAPIError("Did not get a JSON object (check device id)")
            return content
        else:
            raise NinjaAPIError('Got status code %s, expected 200' % (res.status_code,))


    def getDeviceHeartbeat(self, device_guid):
        return self._makeGETRequest(self.DEVICE_ROOT_URL + '/' + device_guid + '/heartbeat')


    def getDeviceURL(self, device_guid):
        return self.DEVICE_ROOT_URL + '/' + device_guid




class Watcher(object):
    def __init__(self, *args):
        self._devices = {}
        for device in args:
            self.watch(device)
        self.active = False
        return super(Watcher, self).__init__()

    def watch(self, device):
        self._devices[device.guid] = device

    def unwatch(self, device):
        self._devices.pop(device.guid)

    def start(self, period=10, duration=float('inf')):
        self.active = True
        self._elapsed = 0

        if not self._devices:
            raise Exception('Watcher instance does not have any devices')

        while self._elapsed < duration:
            self._last_poll = datetime.utcnow()
            for guid, device in self._devices.items():
                device.heartbeat()
            self._elapsed += period
            if duration - self._elapsed > period:
                time.sleep(period)

        self.active = False
