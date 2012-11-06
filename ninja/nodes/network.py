from .core import Node, HasInput, HasOutput

import requests
# class HTTPWriter(Node, HasInput):
#     def __init__(self, *args, **kwargs):
#         super(HTTPWriter, self).__init__(*args, **kwargs)
#         self._opts = kwargs

#     def _validateOptions(self):
#         self._opts
#         return True

#     def setOptions(self, **kwargs):
#         self._opts = kwargs
#         self._validateOptions()

#     def _sendRequest(self, data):
#         self._validateOptions()

#     def receiveData(self, data):
#         self._writeToFile(data)


class HTTPReader(Node, HasOutput):
    def __init__(self, *args, **kwargs):
        super(HTTPReader, self).__init__(*args, **kwargs)
        self._opts = kwargs

    def _validateOptions(self):
        self._opts
        return True

    def setOptions(self, **kwargs):
        self._opts = kwargs
        self._validateOptions()

    def _sendRequest(self):
        response = requests.get(self._opts.get('url'))
        return response.content

    def emitData(self):
        data = self._sendRequest()
        self.o.emit(self.id, data)