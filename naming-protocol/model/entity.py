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

    def generate_index_string(self, num_digit, index_prefix, index):
        return index_prefix + '{{:0{:d}X}}'.format(num_digit).format(index)


class NoneEntity(Entity):
    def __init__(self):
        super().__init__()

    def __iter__(self):
        yield from []

    def get_lengths(self):
        return []

    def represent(self, num_digits, index_prefix, indent, prefix):
        reprs = []
        reprs.append(self.pure_represent(num_digits, index_prefix, indent, prefix))
        return reprs

    def pure_represent(self, num_digits, index_prefix, indent, prefix):
        return indent, prefix, index_prefix + '0' * sum(num_digits), 'None'


class ContentEntity(Entity):
    def __init__(self, content):
        super().__init__()
        self.content = content

    def __iter__(self):
        yield from []

    def get_content(self):
        return self.content

    def get_lengths(self):
        return []

    def represent(self, num_digits, index_prefix, indent, prefix):
        reprs = []
        reprs.append(self.pure_represent(num_digits, index_prefix, indent, prefix))
        return reprs

    def pure_represent(self, num_digits, index_prefix, indent, prefix):
        return indent, prefix, index_prefix + '0' * sum(num_digits), '\'{:s}\''.format(self.content.translate(str.maketrans({'\'': '\\\''})))


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

    def get_lengths(self):
        lengths = []
        for name, value in self:
            child = value.get_lengths()
            for i, x in enumerate(child):
                if len(lengths) == i:
                    lengths.append(x)
                else:
                    assert len(lengths) > i
                    if lengths[i] < x:
                        lengths[i] = x
        return [len(self.nvmap), *lengths]

    def represent(self, num_digits, index_prefix, indent, prefix):
        reprs = []
        reprs.append(self.pure_represent(num_digits, index_prefix, indent, prefix))
        for index, (name, value) in enumerate(self):
            reprs.extend(value.represent(num_digits[1:], self.generate_index_string(num_digits[0], index_prefix, index), indent + 1, '[{:s}]'.format(name)))
        return reprs

    def pure_represent(self, num_digits, index_prefix, indent, prefix):
        return indent, prefix, 'Individual', index_prefix + '-' * sum(num_digits)


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

    def get_lengths(self):
        lengths = []
        for index, value in self:
            child = value.get_lengths()
            for i, x in enumerate(child):
                if len(lengths) == i:
                    lengths.append(x)
                else:
                    assert len(lengths) > i
                    if lengths[i] < x:
                        lengths[i] = x
        return [len(self.internal_list), *lengths]

    def represent(self, num_digits, index_prefix, indent, prefix):
        reprs = []
        reprs.append(self.pure_represent(num_digits, index_prefix, indent, prefix))
        for index, value in self:
            reprs.extend(value.represent(num_digits[1:], self.generate_index_string(num_digits[0], index_prefix, index), indent + 1, '[{:d}]'.format(index)))
        return reprs

    def pure_represent(self, num_digits, index_prefix, indent, prefix):
        return indent, prefix, 'List', index_prefix + '-' * sum(num_digits)


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

    def get_lengths(self):
        lengths = []
        for key, value in self:
            child = value.get_lengths()
            for i, x in enumerate(child):
                if len(lengths) == i:
                    lengths.append(x)
                else:
                    assert len(lengths) > i
                    if lengths[i] < x:
                        lengths[i] = x
        return [len(self.internal_map), *lengths]

    def represent(self, num_digits, index_prefix, indent, prefix):
        reprs = []
        reprs.append(self.pure_represent(num_digits, index_prefix, indent, prefix))
        for index, (key, value) in enumerate(self):
            reprs.extend(value.represent(num_digits[1:], self.generate_index_string(num_digits[0], index_prefix, index), indent + 1, '[\'{:s}\']'.format(key.translate(str.maketrans({'\'': '\\\''})))))
        return reprs

    def pure_represent(self, num_digits, index_prefix, indent, prefix):
        return indent, prefix, 'Group', index_prefix + '-' * sum(num_digits)
