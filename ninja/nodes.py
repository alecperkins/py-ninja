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



class HasInput(object):
    def setupInput(self):
        self.i = Input()
        self.i.setNode(self)

    @property
    def receiveData(self):
        raise NotImplementedError('')

class HasOutput(object):
    def setupOutput(self):
        self.o = Output()
        self.o.setNode(self)

    @property
    def emitData(self):
        raise NotImplementedError('')

class Node(object):
    def __init__(self, label=None, *args, **kwargs):
        self.label = label
        self.id = str(uuid4())
        if hasattr(self, 'setupOutput'):
            self.setupOutput()
        if hasattr(self, 'setupInput'):
            self.setupInput()



# Basic nodes

class Echo(Node, HasInput):
    """
    Public (I): prints the data it receives to stdout.
    """
    def receiveData(self, data):
        label = self.label
        if not label:
            label = 'Echo ' + self.id.split('-')[0]
        print label,':', data


class Emit(Node, HasOutput):
    """
    Public (O): emits a static value, or the return value of a callable.
    """
    def __init__(self, data_to_emit, *args, **kwargs):
        super(Emit, self).__init__(*args, **kwargs)
        self._data_to_emit = data_to_emit

    def emitData(self):
        if hasattr(self._data_to_emit, '__call__'):
            d = self._data_to_emit()
        else:
            d = self._data_to_emit
        self.o.emit(d)


class Counter(Node, HasOutput):
    """
    Public (O): emits a counter value, or the return value of a callable.
    (The callable is given the current value of the counter.)
    """
    def emitData(self):
        for i in range(self._count_to):
            if self._data_to_emit:
                if hasattr(self._data_to_emit, '__call__'):
                    d = self._data_to_emit(i)
                else:
                    d = self._data_to_emit
            else:
                d = i
            self.o.emit(d)
            time.sleep(self._delay)

    def startCounter(self, to=10, delay=1, data=None):
        self._count_to = to
        self._delay = delay
        self._data_to_emit = data
        self.emitData()




class Channel(Node, HasInput, HasOutput):
    """
    Public (I/O): pass-through node, immediately emits all data it receives.

    Useful for aggregating inputs and/or outputs into a single point. Can be
    given a transform function, which will be called on the data every time.
    """
    def __init__(self, *args, **kwargs):
        super(Channel, self).__init__(*args, **kwargs)
        self._transform = kwargs.get('transform', None)

    def receiveData(self, data):
        if self._transform:
            data = self._transform(data)
        self.o.emit(data)

    def setTransform(self, fn):
        self._transform = fn

    def clearTransform(self, fn):
        self._transform = None

import csv
class CSVWriter(Node, HasInput):
    def __init__(self, *args, **kwargs):
        super(CSVWriter, self).__init__(*args, **kwargs)
        self._file = kwargs.get('file', None)
        if not self._file:
            raise ValueError('file not specified')

        self._write_mode = kwargs.get('mode', 'a')

        self._headers = kwargs.get('headers', None)
        if self._headers:
            self._writeToFile(self._headers, mode='w')

    def _writeToFile(self, data, mode=None):
        if not mode:
            mode = self._write_mode
        with open(self._file, mode) as f:
            writer = csv.writer(f)
            writer.writerow(data)

    def receiveData(self, data):
        self._writeToFile(data)
