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


    def receiveData(self, data):
        if self._test(data):
            self.o.emit(data)
        else:
            self.fail.emit(data)

