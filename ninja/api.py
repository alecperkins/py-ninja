import json
import requests
import time

from datetime   import datetime
from exceptions import Exception, ValueError

from .devices import TYPE_MAP, Device



class NinjaAPIError(Exception):
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            self.status_code = args[1]
        super(NinjaAPIError, self).__init__(*args, **kwargs)



class NinjaAPI(object):
    """
    Carries authentication information
    """

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

    def _makePOSTRequest(self, url, data):
        params = {
            'user_access_token': self.access_token,
        }
        res = requests.post(url, params=params, data=data)
        if res.status_code == 200:
            try:
                content = json.loads(res.content)
            except ValueError:
                raise NinjaAPIError("Did not get a JSON object (check device id)")
            if content['id'] != 0:
                raise NinjaAPIError('Got status code %s, expected 200' % (content['id'],), content['id'])    
            return content
        else:
            raise NinjaAPIError('Got status code %s, expected 200' % (res.status_code,), res.status_code)

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

    def _makeDELETERequest(self, url):
        params = {
            'user_access_token': self.access_token,
        }
        res = requests.delete(url, params=params)   

        if res.status_code == 200:
            try:
                content = json.loads(res.content)
            except ValueError:
                raise NinjaAPIError("Did not get a JSON object (check device id)")
            return content
        else:
            raise NinjaAPIError('Got status code %s, expected 200' % (res.status_code,))

    def getDeviceHeartbeat(self, device_guid):
        return self._makeGETRequest(self.getDeviceHeartbeatURL(device_guid))

    def getDeviceURL(self, device_guid):
        return self.DEVICE_ROOT_URL + '/' + device_guid

    def getDeviceHeartbeatURL(self, device_guid):
        return self.getDeviceURL(device_guid) + '/heartbeat'

    def getDeviceCallbackURL(self, device_guid):
        return self.getDeviceURL(device_guid) + '/callback'

    def getDevices(self):
        response = self._makeGETRequest(self.DEVICES_URL)
        devices = []
        for guid, device_info in response['data'].items():
            device_class = TYPE_MAP.get(device_info.get('device_type'), Device)
            device = device_class(self, guid, device_info)
            devices.append(device)
        return devices

    def getDevice(self, guid):
        # Need to get the whole device list because the API is not so great.
        response = self._makeGETRequest(self.DEVICES_URL)
        device_info = response['data'][guid]
        device_class = TYPE_MAP.get(device_info.get('device_type'), Device)
        return device_class(self, guid, device_info)

    def getUser(self):
        user_info = self._makeGETRequest(self.USER_URL)
        return User(user_info)

    def setDeviceWebhookURL(self, device_guid, url):
        callback_endpoint = self.getDeviceCallbackURL(device_guid)
        try:
            return self._makePOSTRequest(callback_endpoint, data={ 'url': url })
        except NinjaAPIError as e:
            if e.status_code == 409: # Already exists, so update it.
                return self._makePUTRequest(callback_endpoint, data={ 'url': url })
            else:
                raise e
        return

    def getDeviceWebhookURL(self, device_guid):
        return self._makeGETRequest(self.getDeviceCallbackURL(device_guid)).get('data', {}).get('url')

    def clearDeviceWebhookURL(self, device_guid):
        return self._makeDELETERequest(self.getDeviceCallbackURL(device_guid))


class User(object):
    def __init__(self, user_info):
        self.id = user_info.get('id')
        self.name = user_info.get('name')
        self.email = user_info.get('email')
        self.pusher_channel = user_info.get('pusherChannel')



class Watcher(object):
    def __init__(self, *args, **kwargs):
        self._devices = {}
        for device in args:
            self.watch(device)
        self.active = False
        self._post_cycle = kwargs.get('post_cycle')
        self._pre_cycle = kwargs.get('pre_cycle')
        return super(Watcher, self).__init__()

    def watch(self, device):
        self._devices[device.guid] = device

    def unwatch(self, device):
        self._devices.pop(device.guid)

    def start(self, period=10, duration=float('inf'), silent=False):
        self.active = True
        self._elapsed = 0

        if not self._devices:
            raise Exception('Watcher instance does not have any devices')

        while self._elapsed < duration:
            if self._pre_cycle:
                self._pre_cycle()

            self._last_poll = datetime.utcnow()
            for guid, device in self._devices.items():
                # TODO: This is the point to geventify. Heartbeats need to be made async.
                device.heartbeat(silent=silent)
            self._elapsed += period

            if self._post_cycle:
                self._post_cycle()

            if duration - self._elapsed > period:
                time.sleep(period)

        self.active = False


