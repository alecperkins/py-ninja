import time
from uuid       import uuid4

from ninja.api  import Watcher


class NodeConnector(object):

    def __init__(self):
        self.connected = {}

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
            self.connected[connector.id] = connector
            if reciprocal:
                connector.connect(self, reciprocal=False)

    def disconnect(self, *args, **kwargs):
        reciprocal = kwargs.get('reciprocal', True)
        for connector in args:
            if not connector.id in self._connected:
                raise Exception('%s not connected' % (connector.id,))
            del self.connected[connector.id]
            if reciprocal:
                connector.disconnect(self, reciprocal=False)


class Input(NodeConnector):
    def __call__(self, data, from_id=None):
        self.node.receiveData(data, from_id)
        self.node.last_data = data
        return self

    def readAll(self):
        return [self._connected[id]() for id in self._connected]


class Output(NodeConnector):
    def __call__(self):
        return self.node.last_data

    def emit(self, data):
        self.node.last_data = data
        for input_id, i in self.connected.items():
            i(data, from_id=self.id)



# Node mixins

class HasInput(object):
    def setupInput(self):
        self.attachConnector('i', Input)

    @property
    def receiveData(self, data, from_id):
        raise NotImplementedError('')

class HasOutput(object):
    def setupOutput(self):
        self.attachConnector('o', Output)

    @property
    def emitData(self):
        raise NotImplementedError('')



# Base Node object

class Node(object):

    def __init__(self, label=None, *args, **kwargs):
        self.label = label
        self.id = str(uuid4())
        self.last_data = None
        if self.hasOutput():
            self.setupOutput()
        if self.hasInput():
            self.setupInput()

    def hasOutput(self):
        return hasattr(self, 'setupOutput')

    def hasInput(self):
        return hasattr(self, 'setupInput')

    def attachConnector(self, attr, connector_class):
        connector = connector_class()
        setattr(self, attr, connector)
        connector.setNode(self)



class Ticker(object):
    """
    
    """
    def __init__(self, *args, **kwargs):
        self._nodes = {}
        self._watcher = Watcher(post_cycle=self._doEmits)
        for node in args:
            self.watch(node)
        return super(Ticker, self).__init__()

    def _doEmits(self):
        for node_id in self._nodes:
            self._nodes[node_id].emitData()

    def start(self, period=10, duration=float('inf')):
        self._watcher.start(period=period, duration=duration, silent=True)

    def watch(self, node):
        self._nodes[node.id] = node
        if hasattr(node, 'device'):
            self._watcher.watch(node.device)

