import argparse
import sys
from .parser import *
from .cst2ast import CST2AST
from .model import Model, Context, ModuleBuilder
from .execution import ExecutionModel


class Opts:
    @classmethod
    def parse(cls, *argv):
        program, *arguments = argv
        parser = argparse.ArgumentParser(prog=program)
        parser.add_argument('-i', '--input', default=None, help='The path to the input file. Use stdin by default.')
        parser.add_argument('-d', '--dep', action='append', default=[], help='Imported file.')
        parser.add_argument('-o', '--output', default=None, help='The path to the output file. Use stdout by default.')
        return cls(**parser.parse_args(arguments).__dict__)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def open(self):
        if self.output is None:
            self.output = sys.stdout
        else:
            self.output = open(self.output, 'w')

        return self

    def close(self):
        self.output.close()


def analyze_file(execution_model, filename):
    print('Analyze file \'{:s}\'.'.format(filename))
    parser = FileParser(filename)
    tree = parser.parse()
    stmts = CST2AST(parser.input_stream).visit(tree)

    for stmt in stmts:
        execution_model.visit(stmt)
    print('Done.')


def main(argv):
    opts = Opts.parse(*argv)

    opts.open()

    model = Model()
    module_builder = ModuleBuilder()
    context = Context(module_builder)
    execution_model = ExecutionModel(model, context)

    for dependency in opts.dep:
        analyze_file(execution_model, dependency)
        print()

    print('Read input.')
    if opts.input is None:
        parser = StdinParser()
        tree = parser.parse()
    else:
        parser = FileParser(opts.input)
        tree = parser.parse()
    stmts = CST2AST(parser.input_stream).visit(tree)

    for stmt in stmts:
        execution_model.visit(stmt)

    opts.close()


if __name__ == '__main__':
    main(sys.argv)
