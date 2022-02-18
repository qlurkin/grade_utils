from io import StringIO
import sys

class Capture(list):
    def __enter__(self):
        self.__stdout = sys.stdout
        sys.stdout = self.__stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self.__stringio.getvalue().splitlines())
        self.__stringio.close()
        sys.stdout = self.__stdout
    def getvalue(self):
        return '\n'.join(self)