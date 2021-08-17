import collections
from .entity import *


__all__ = [
    'Root',
    'Package',
    'ModuleBuilder',
    'Module',
    'GroupBuilder',
    'ScopeProcessor'
]


class Holder:
    def __init__(self):
        pass

    def get_by_name(self, name):
        raise NotImplementedError

    def get_by_index(self, index):
        raise NotImplementedError

    def get_by_key(self, key):
        raise NotImplementedError


class Root(Holder):
    def __init__(self):
        self.children = dict()


class Package(Holder):
    def __init__(self):
        self.module = None
        self.children = dict()

    def set_module(self, path, module):
        assert self.module is None, 'Path \'{:s}\' has already been occupied.'.format('.'.join(path))
        self.module = module


class ModuleBuilder(Holder):
    def __init__(self, root):
        self.root = root
        self.path = None
        self.nvmap = collections.OrderedDict()
        self.field_map = collections.OrderedDict()

    def get_scope_path(self):
        return []

    def get_by_name(self, name):
        return self.nvmap[name]

    def set_by_name(self, name, value):
        self.nvmap[name] = value

    def set_path(self, path):
        assert self.path is None, 'Path has already been set to \'{:s}\'.'.format('.'.join(path))
        self.path = path

    def set_key_value(self, key, value):
        self.nvmap[key] = value

    def set_field(self, key, value):
        self.field_map[key] = value

    def build(self):
        module = Module(self.field_map)
        package = self.root
        for token in self.path:
            if token not in package.children:
                package.children[token] = Package()
            package = package.children[token]
        package.set_module(self.path, module)
        return module


class Module(Holder):
    def __init__(self, field_map):
        self.field_map = field_map


class GroupBuilder(Holder):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.nvmap = collections.OrderedDict()
        self.kvmap = collections.OrderedDict()

    def get_by_name(self, name):
        if name == self.name:
            return self
        else:
            if name in self.nvmap:
                return self.nvmap[name]
            else:
                return self.parent.get(name)

    def set_by_name(self, name, value):
        self.nvmap[name] = value

    def get_by_key(self, key):
        return self.kvmap[key]

    def set_by_key(self, key, value):
        self.kvmap[key] = value

    def unzip(self, entity):
        assert isinstance(entity, GroupEntity)
        for key, value in entity.items():
            self.set_by_key(key, value)

    def build(self):
        entity = GroupEntity()
        for key, value in self.kvmap.items():
            entity.set_by_key(key, value)
        return entity


class ScopeProcessor(Holder):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.nvmap = collections.OrderedDict()
        self.kvmap = collections.OrderedDict()
        self.used_set = []
        self.names = set()

    def get_scope_path(self):
        return [*self.parent.get_scope_path(), self.name]

    def get_by_name(self, name):
        if name == self.name:
            return self
        else:
            if name in self.nvmap:
                return self.nvmap[name]
            else:
                return self.parent.get_by_name(name)

    def set_by_name(self, name, value):
        self.nvmap[name] = value

    def get_by_key(self, key):
        return self.kvmap[key]

    def set_by_key(self, key, value):
        self.kvmap[key] = value

    def add(self, name):
        self.names.add(name)

    def remove(self, name):
        self.names.remove(name)

    def unzip(self, entity):
        assert isinstance(entity, GroupEntity)
        for key, value in entity.items():
            self.use(value)

    def use(self, entity):
        self.used_set.append(entity)

    def check_existence(self, name):
        assert name not in self.names, 'Name \'{:s}\' already exists.'.format(name)
        if isinstance(self.parent, ScopeProcessor):
            self.parent.check_existence(name)

    def validate(self, model, output=True):
        if output:
            print('Scope:', '.'.join(self.get_scope_path()))
        disabled_set = set()
        for name in model.expand(self.used_set, disabled_set):
            if output:
                print('validate:', name)
            self.check_existence(name)
            self.names.add(name)

    def invalidate(self, model, output=True):
        if output:
            print('Scope:', '.'.join(self.get_scope_path()))
        disabled_set = set()
        for name in model.expand(self.used_set, disabled_set):
            if output:
                print('invalidate:', name)
            assert name in self.names, 'Name \'{:s}\' does not exist.'.format(name)
            self.names.remove(name)
