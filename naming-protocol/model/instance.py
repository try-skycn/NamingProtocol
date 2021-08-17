from .entity import *


__all__ = [
    'NameLeftSubscript',
    'IndexLeftSubscript',
    'KeyLeftSubscript',
    'LeftIndividualEntitySubscript',
    'LeftListEntitySubscript',
    'LeftGroupEntitySubscript',
    'LeftModuleBuilderSubscript',
    'LeftGroupBuilderSubscript',
    'LeftScopeProcessorSubscript'
]


class Subscript:
    def __init__(self):
        pass


class NameLeftSubscript(Subscript):
    def __init__(self, name):
        super().__init__()
        self.name = name


class IndexLeftSubscript(Subscript):
    def __init__(self, index):
        super().__init__()
        self.index = index


class KeyLeftSubscript(Subscript):
    def __init__(self, key):
        super().__init__()
        self.key = key


class LeftInstance:
    def __init__(self):
        pass


class LeftEntitySubscript(LeftInstance):
    def __init__(self, entity, subscript):
        super().__init__()
        assert isinstance(entity, Entity)
        self.entity = entity
        self.subscript = subscript


class LeftIndividualEntitySubscript(LeftEntitySubscript):
    def __init__(self, entity, subscript):
        assert isinstance(subscript, NameLeftSubscript)
        super().__init__(entity, subscript)

    def set(self, value):
        name = self.subscript.name
        self.entity.set_by_name(name, value)


class LeftListEntitySubscript(LeftEntitySubscript):
    def __init__(self, entity, subscript):
        assert isinstance(subscript, IndexLeftSubscript)
        super().__init__(entity, subscript)

    def set(self, value):
        index = self.subscript.index
        assert 0 <= index and index < entity.length
        self.entity.set_by_index(index, value)
        

class LeftGroupEntitySubscript(LeftEntitySubscript):
    def __init__(self, entity, subscript):
        assert isinstance(subscript, KeyLeftSubscript)
        super().__init__(entity, subscript)

    def set(self, value):
        key = self.subscript.key
        self.entity.set_by_key(key, value)


class LeftModuleBuilderSubscript(LeftInstance):
    def __init__(self, module_builder, subscript):
        assert isinstance(subscript, NameLeftSubscript)
        self.module_builder = module_builder
        self.subscript = subscript

    def set(self, value):
        name = self.subscript.name
        self.module_builder.set_by_name(name, value)


class LeftGroupBuilderSubscript(LeftInstance):
    def __init__(self, group_builder, subscript):
        assert isinstance(subscript, NameLeftSubscript) or isinstance(subscript, KeyLeftSubscript)
        self.group_builder = group_builder
        self.subscript = subscript

    def set(self, value):
        if isinstance(self.subscript, NameLeftSubscript):
            name = self.subscript.name
            self.group_builder.set_by_name(name, value)
        elif isinstance(self.subscript, KeyLeftSubscript):
            key = self.subscript.key
            self.group_builder.set_by_key(key, value)
        else:
            raise TypeError()


class LeftScopeProcessorSubscript(LeftInstance):
    def __init__(self, scope_processor, subscript):
        assert isinstance(subscript, NameLeftSubscript) or isinstance(subscript, KeyLeftSubscript)
        self.scope_processor = scope_processor
        self.subscript = subscript

    def set(self, value):
        if isinstance(self.subscript, NameLeftSubscript):
            name = self.subscript.name
            self.scope_processor.set_by_name(name, value)
        elif isinstance(self.subscript, KeyLeftSubscript):
            key = self.subscript.key
            self.scope_processor.set_by_key(key, value)
        else:
            raise TypeError()
