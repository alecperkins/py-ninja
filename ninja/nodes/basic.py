import time
from .core import Node, HasInput, HasOutput

# Basic nodes

class Echo(Node, HasInput):
    """
    Public (I): prints the data it receives to stdout.
    """
    def __init__(self, *args, **kwargs):
        super(Echo, self).__init__(*args, **kwargs)
        self._message = kwargs.get('message', '')

    def setMessage(self, message):
        self._message = message

    def receiveData(self, data, from_id):
        label = self.label
        if not label:
            label = 'Echo ' + self.id.split('-')[0]
        print label,':', self._message, data


class Source(Node, HasOutput):
    """
    Public (O): emits a static value, or the return value of a callable.
    """
    def __init__(self, data_to_emit, *args, **kwargs):
        super(Source, self).__init__(*args, **kwargs)
        self._data_to_emit = data_to_emit

    def emitData(self):
        if hasattr(self._data_to_emit, '__call__'):
            d = self._data_to_emit()
        else:
            d = self._data_to_emit
        self.o.emit(d)


class Sink(Node, HasInput):
    """
    Public (I): receives data, passing it to a callable.
    """
    def __init__(self, *args, **kwargs):
        super(Sink, self).__init__(*args, **kwargs)
        self._onReceive = kwargs.get('on_receive')
        if not self._onReceive:
            raise ValueError('on_receive must be specified')

    def receiveData(self, data, from_id):
        self._onReceive(data)


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

    def receiveData(self, data, from_id):
        if self._transform:
            data = self._transform(data)
        self.o.emit(data)

    def setTransform(self, fn):
        self._transform = fn

    def clearTransform(self, fn):
        self._transform = None



class Buffer(Channel):
    def __init__(self, *args, **kwargs):
        super(Buffer, self).__init__(*args, **kwargs)
        self._queue = []
        self._keep = kwargs.get('keep', None)
        self._flush_at = kwargs.get('flush_at', None)
        if self._keep is not None and self._flush_at is not None:
            raise ValueError('Either keep or flush_at may be specified, but not both.')

        if self._keep is not None:
            if self._keep <= 0:
                raise ValueError('keep must be an int greater than 0')
        else:
            self._keep = float('inf')

        if self._flush_at is not None:
            if self._flush_at <= 0:
                raise ValueError('flush_at must be an int greater than 0')
        else:
            self._flush_at = float('inf')

    def receiveData(self, data, from_id):
        if self._transform:
            data = self._transform(data)
        self._queue.append(data)

        # `keep` and `flush_at` are exclusive, so only one of these will happen, if any.
        if len(self._queue) >= self._flush_at:
            self.flush()
        if len(self._queue) > self._keep:
            self._queue = self._queue[1:]

    def flush(self):
        for data in self._queue:
            self.o.emit(data)
        self._queue = []




