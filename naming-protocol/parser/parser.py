from antlr4 import *
from ..grammar import NamingProtocolLexer, NamingProtocolParser


__all__ = [
    'StdinParser',
    'StringParser',
    'FileParser'
]


class Parser(NamingProtocolParser):
    def __init__(self, input_stream):
        lexer = NamingProtocolLexer(input_stream)
        stream = CommonTokenStream(lexer)
        super().__init__(stream)
        self.input_stream = input_stream

    def parse(self):
        raise NotImplementedError


class StdinParser(Parser):
    def __init__(self):
        super().__init__(StdinStream())


class StringParser(Parser):
    def __init__(self, content):
        super().__init__(InputStream(content))


class FileParser(Parser):
    def __init__(self, fpath):
        assert isinstance(fpath, str)
        super().__init__(FileStream(fpath))

    def parse(self):
        return self.fileInput()
