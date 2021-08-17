import argparse
import sys
from .parser import *
from .cst2ast import CST2AST
from .model import Context, Root, ModuleBuilder
from .execution import ExecutionModel


class Opts:
    @classmethod
    def parse(cls, *argv):
        program, *arguments = argv
        parser = argparse.ArgumentParser(prog=program)
        parser.add_argument('-i', '--input', default=None, help='The path to the input file. Use stdin by default.')
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


def main(argv):
    opts = Opts.parse(*argv)

    opts.open()
    if opts.input is None:
        parser = StdinParser()
        tree = parser.parse()
    else:
        parser = FileParser(opts.input)
        tree = parser.parse()
    stmts = CST2AST(parser.input_stream).visit(tree)

    model = Model()
    root = Root()
    module_builder = ModuleBuilder(root)
    context = Context(module_builder)
    execution_model = ExecutionModel(model, context)
    for stmt in stmts:
        execution_model.visit(stmt)
    opts.close()


from .model.entity import *
from .model.model import *


def test(argv):
    model = Model()
    group_entity = GroupEntity()

    individual_entity = IndividualEntity('function')
    model.group_add(group_entity, individual_entity)

    individual_entity = IndividualEntity('parameter')
    individual_entity.plural = IndividualEntity('parameters')
    model.group_add(group_entity, individual_entity)

    head = IndividualEntity('head')
    output = model.cross(head, group_entity, '_', plural='original-plural')

    for name in output:
        print(name)


if __name__ == '__main__':
    main(sys.argv)
