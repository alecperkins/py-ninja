import time
from uuid import uuid4



class NodeConnector(object):

    def __init__(self):
        self._connected = {}

    @property
    def id(self):
        return self.node.id

    def setNode(self, node):
        self.node = node

    def connect(self, *args, **kwargs):
        reciprocal = kwargs.get('reciprocal', True)
        for connector in args:
            if isinstance(connector, self.__class__):
                raise Exception('Cannot connect %s to %s' % (type(connector), type(self)))
            self._connected[connector.id] = connector
            if reciprocal:
                connector.connect(self, reciprocal=False)

    def disconnect(self, *args, **kwargs):
        reciprocal = kwargs.get('reciprocal', True)
        for connector in args:
            if not connector.id in self._connected:
                raise Exception('%s not connected' % (connector.id,))
            del self._connected[connector.id]
            if reciprocal:
                connector.disconnect(self, reciprocal=False)


class Input(NodeConnector):
    def __call__(self, data):
        self.node.receiveData(data)
        self.node.last_data = data
        return self



class Output(NodeConnector):
    def __call__(self):
        return self.node.last_data

    def emit(self, data):
        self.node.last_data = data
        for input_id, input in self._connected.items():
            input(data)



# Node mixins

class HasInput(object):
    def setupInput(self):
        self.attachConnector('i', Input)

    @property
    def receiveData(self):
        raise NotImplementedError('')

class HasOutput(object):
    def setupOutput(self):
        self.attachConnector('o', Output)

    @property
    def emitData(self):
        raise NotImplementedError('')



# Base Node object

class Node(object):

    def attachConnector(self, attr, connector_class):
        connector = connector_class()
        setattr(self, attr, connector)
        connector.setNode(self)

    def __init__(self, label=None, *args, **kwargs):
        self.label = label
        self.id = str(uuid4())
        if self.hasOutput():
            self.setupOutput()
        if self.hasInput():
            self.setupInput()

    def hasOutput(self):
        return hasattr(self, 'setupOutput')

    def hasInput(self):
        return hasattr(self, 'setupInput')


