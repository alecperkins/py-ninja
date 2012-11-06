from .core import Node, HasInput, HasOutput, Output

class If(Node, HasInput, HasOutput):
    def __init__(self, *args, **kwargs):
        super(If, self).__init__(*args, **kwargs)
        self._test = kwargs.get('test')
        if not self._test:
            raise ValueError('test not specified')
        elif not hasattr(self._test, '__call__'):
            raise ValueError('test must be a callable')

        self.attachConnector('fail', Output)

    def receiveData(self, data, from_id):
        if self._test(data):
            self.o.emit(data)
        else:
            self.fail.emit(data)


from .basic import Channel

# Waits until it receives data from every connected output, then emits the entire set at once.
class And(Channel):
    def __init__(self, *args, **kwargs):
        super(And, self).__init__(*args, **kwargs)
        self._data_set = {}

    def receiveData(self, data, from_id):
        self._data_set[from_id] = data
        if len(self._data_set) == len(self.i.connected):
            self.o.emit(self._data_set)
            self._data_set = {}

