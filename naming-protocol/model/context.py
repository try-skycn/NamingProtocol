from .model import *
from .package import *
from .instance import *


class Context:
    def __init__(self, module_builder):
        self.stack = [module_builder]

    def is_module_builder(self):
        holder = self.top()
        return isinstance(holder, ModuleBuilder)

    def is_group_builder(self):
        holder = self.top()
        return isinstance(holder, GroupBuilder)

    def is_scope_processor(self):
        holder = self.top()
        return isinstance(holder, ScopeProcessor)

    def push_group_builder(self, name):
        assert self.is_module_builder() or self.is_group_builder() or self.is_scope_processor()
        group_builder = GroupBuilder(self.top(), name)
        self.stack.append(group_builder)
        return group_builder

    def push_scope_processor(self, name):
        assert self.is_module_builder() or self.is_scope_processor()
        scope_processor = ScopeProcessor(self.top(), name)
        self.stack.append(scope_processor)
        return scope_processor

    def top(self):
        return self.stack[-1]

    def get_by_name(self, name):
        return self.top().get_by_name(name)

    def set_by_name(self, name, value):
        return self.top().set_by_name(name, value)

    def get_by_key(self, key):
        return self.top().get_by_key(key)

    def set_by_key(self, key, value):
        return self.top().set_by_key(key, value)

    def set_entity(self, entity):
        if isinstance(entity, IndividualEntity):
            self.set_by_key(entity.get_content(), entity)
        elif isinstance(entity, ContentEntity):
            self.set_by_key(entity.content, entity)
        else:
            raise TypeError()

    def pop(self):
        return self.stack.pop()

    def left_subscript(self, subscript):
        holder = self.top()
        if isinstance(holder, ModuleBuilder):
            return LeftModuleBuilderSubscript(holder, subscript)
        elif isinstance(holder, GroupBuilder):
            return LeftGroupBuilderSubscript(holder, subscript)
        elif isinstance(holder, ScopeProcessor):
            return LeftScopeProcessorSubscript(holder, subscript)
        else:
            raise TypeError()
