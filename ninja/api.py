from exceptions import Exception, ValueError

import json
import requests
import time


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


    def _makeRequest(self, url, binary=False):

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


    def updateDevice(self, device_guid):
        return self._makeRequest(self.DEVICE_ROOT_URL + '/' + device_guid + '/heartbeat')



class Watcher(object):
    def __init__(self, *args, **kwargs):
        self._devices = {}
        self.active = False
        super(Watcher, self).__init__(*args, **kwargs)

    def watch(self, device):
        self._devices[device.guid] = device

    def unwatch(self, device):
        self._devices.pop(device.guid)

    def start(self, period=10):
        self.active = True
        if not self._devices:
            raise Exception('Watcher instance does not have any devices')

        while self.active:
            for guid, device in self._devices.items():
                device.heartbeat()
            time.sleep(period)

    def quit(self):
        self.active = False
