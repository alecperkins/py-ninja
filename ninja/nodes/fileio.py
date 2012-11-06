from .core import Node, HasInput, HasOutput

class FileWriter(Node, HasInput):
    pass

class FileReader(Node, HasOutput):
    pass
    # emitData() - reads and emits
    # .o() - reads and returns


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

    def receiveData(self, data, from_id):
        self._writeToFile(data)


# {
#     'file': 'filename.json',
#     'data': {}
# }
import json
class JSONWriter(Node, HasInput):
    def _writeToFile(self, file_name, data_to_write):
        file(file_name, 'w').write(json.dumps(data_to_write))

    def receiveData(self, data, from_id):
        file_name       = data.get('file')
        data_to_write   = data.get('data')
        if not file_name:
            raise ValueError('file not specified')
        self._writeToFile(file_name, data_to_write)

class JSONReader(Node, HasOutput):
    pass
