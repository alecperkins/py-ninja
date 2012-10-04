


class Events(object):
    def __init__(self):
        self._callbacks = {}

    # Bind to events
    def on(self, event, callback):
        if not event in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
        return self

    def off(self, event):
        self._callbacks[event] = []
        return self

    def _fire(self, event, *args, **kwargs):
        callbacks = self._callbacks.get(event, [])
        for callback in callbacks:
            callback(self, *args, **kwargs)


