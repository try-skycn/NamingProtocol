import collections


class Entity:
    def __init__(self):
        self.mutable = True

    def get_content(self):
        raise NotImplementedError

    def get_by_name(self, name):
        raise NotImplementedError

    def get_by_index(self, index):
        raise NotImplementedError

    def get_by_key(self, key):
        raise NotImplementedError


class NoneEntity(Entity):
    def __init__(self):
        super().__init__()

    def __iter__(self):
        yield from []

    def represent(self, indent, prefix):
        reprs = []
        reprs.append(self.pure_represent(indent, prefix))
        return reprs

    def pure_represent(self, indent, prefix):
        return indent, prefix, 'None', ''


class ContentEntity(Entity):
    def __init__(self, content):
        super().__init__()
        self.content = content

    def __iter__(self):
        yield from []

    def get_content(self):
        return self.content

    def represent(self, indent, prefix):
        reprs = []
        reprs.append(self.pure_represent(indent, prefix))
        return reprs

    def pure_represent(self, indent, prefix):
        return indent, prefix, 'Content', '\'{:s}\''.format(self.content.translate(str.maketrans({'\'': '\\\''})))


class IndividualEntity(Entity):
    def __init__(self):
        super().__init__()
        self.nvmap = collections.OrderedDict()

    def get_content(self):
        return self.nvmap['original'].get_content()

    def get_by_name(self, name, default=None):
        if default is None:
            return self.nvmap[name]
        else:
            return self.nvmap.get(name, default)

    def set_by_name(self, name, value):
        self.nvmap[name] = value

    def __iter__(self):
        yield from self.nvmap.items()

    def represent(self, indent, prefix):
        reprs = []
        reprs.append(self.pure_represent(indent, prefix))
        for name, value in self:
            reprs.extend(value.represent(indent + 1, '[{:s}]'.format(name)))
        return reprs

    def pure_represent(self, indent, prefix):
        return indent, prefix, 'Individual', '<0x{:X}>'.format(id(self))


class ListEntity(Entity):
    def __init__(self):
        super().__init__()
        self.internal_list = list()

    def append(self, value):
        self.internal_list.append(value)

    def length(self):
        return len(self.internal_list)

    def get_by_index(self, index):
        assert 0 <= index and index < len(self.internal_list)
        return self.internal_list[index]

    def __iter__(self):
        yield from enumerate(self.internal_list)

    def represent(self, indent, prefix):
        reprs = []
        reprs.append(self.pure_represent(indent, prefix))
        for key, value in self:
            reprs.extend(value.represent(indent + 1, '[{:d}]'.format(index)))
        return reprs

    def pure_represent(self, indent, prefix):
        return indent, prefix, 'List', '<0x{:X}>'.format(id(self))


class GroupEntity(Entity):
    def __init__(self):
        super().__init__()
        self.internal_map = collections.OrderedDict()

    def set_by_key(self, key, value):
        self.internal_map[key] = value

    def items(self):
        yield from self.internal_map.items()

    def get_by_key(self, key):
        return self.internal_map[key]

    def __iter__(self):
        yield from self.internal_map.items()

    def represent(self, indent, prefix):
        reprs = []
        reprs.append(self.pure_represent(indent, prefix))
        for key, value in self:
            reprs.extend(value.represent(indent + 1, '[\'{:s}\']'.format(key.translate(str.maketrans({'\'': '\\\''})))))
        return reprs

    def pure_represent(self, indent, prefix):
        return indent, prefix, 'Group', '<0x{:X}>'.format(id(self))
