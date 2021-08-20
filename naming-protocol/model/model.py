import collections
from .entity import *
from .instance import *


class Model:
    def __init__(self):
        pass

    # Cross-Related Methods - START

    def cross_individual(self, left, right, connection, choices):
        if isinstance(left, NoneEntity) or isinstance(right, NoneEntity):
            return NoneEntity()

        if isinstance(left, ContentEntity) and isinstance(right, ContentEntity):
            return ContentEntity(left.content + connection + right.content)

        if isinstance(left, ContentEntity):
            left_backup = left
            left = IndividualEntity()
            left.set_by_name('original', left_backup)

        if isinstance(right, ContentEntity):
            right_backup = right
            right = IndividualEntity()
            right.set_by_name('original', right_backup)

        output = IndividualEntity()

        choices_dict = {name: (left_choice, right_choice) for name, left_choice, right_choice in choices}
        choices_dict.setdefault('original', ('original', 'original'))
        for name, (left_choice, right_choice) in choices_dict.items():
            output.set_by_name(name, self.cross_individual(left.get_by_name(left_choice, NoneEntity()), right.get_by_name(right_choice, NoneEntity()), connection, choices))

        return output

    def cross_right(self, mapping, left, right, connection, choices):
        if isinstance(right, NoneEntity):
            output = NoneEntity()
        elif isinstance(right, ContentEntity) or isinstance(right, IndividualEntity):
            output = self.cross_individual(left, right, connection, choices)
        elif isinstance(right, ListEntity):
            output = ListEntity()
            for value in right.internal_list.items():
                output.append(self.cross_right(mapping, left, value, connection, choices))
        elif isinstance(right, GroupEntity):
            output = GroupEntity()
            for key, value in right.internal_map.items():
                output.set_by_key(key, self.cross_right(mapping, left, value, connection, choices))
        else:
            raise TypeError('Unrecognized entity type \'{:s}\'.'.format(type(right)))

        mapping[right] = output

        return output

    def cross_left(self, mapping, left, right, connection, choices):
        if isinstance(left, NoneEntity):
            output = NoneEntity()
        elif isinstance(left, ContentEntity) or isinstance(left, IndividualEntity):
            output = self.cross_right(dict(), left, right, connection, choices)
        elif isinstance(left, ListEntity):
            output = ListEntity()
            for value in left.internal_list:
                output.append(self.cross_left(mapping, value, right, connection, choices))
        elif isinstance(left, GroupEntity):
            output = GroupEntity()
            for key, value in left.internal_map.items():
                output.set_by_key(key, self.cross_left(mapping, value, right, connection, choices))
        else:
            raise TypeError('Unrecognized entity type \'{:s}\'.'.format(type(left)))

        mapping[left] = output

        return output

    def cross_recursive(self, mapping, left, right, connection, choices):
        return self.cross_left(mapping, left, right, connection, choices)

    def cross(self, left, right, connection, choices):
        return self.cross_recursive(dict(), left, right, connection, choices)

    # Cross-Related Methods - END

    # Public Methods

    def create_none_entity(self):
        return NoneEntity()

    def create_content_entity(self, content):
        return ContentEntity(content)

    def create_individual_entity(self, pairs):
        entity = IndividualEntity()
        for name, value in pairs:
            entity.set_by_name(name, value)
        return entity

    def create_list_entity(self, length):
        list_entity = ListEntity()
        num_digits = count_hex_length(length)
        for i in range(length):
            list_entity.append(ContentEntity('x{:X}'.format(i)))

    def create_group_entity(self, pairs):
        entity = GroupEntity()
        for key, value in pairs:
            entity.set_by_key(key, value)
        return entity

    def collapse(self, center, others):
        return CollapseEntity(center, NoneEntity(), others)

    def keep(self, pairs):
        keep = None
        others = []
        for indicator, child in node.pairs:
            if indicator:
                assert keep is None
                keep = child
            others.append(child)
        return CollapseEntity(keep, keep, others)

    def group_union(self, children, keeps):
        entity = GroupEntity()
        for i, child in enumerate(children):
            assert isinstance(child, GroupEntity)
            for key, value in child:
                if key not in keeps or keeps[key] == i:
                    entity.set_by_key(key, value)
        return entity

    def group_filter(self, body, filter_trailer):
        return filter_trailer.apply(None, body)

    def expand(self, used_set, disabled_set):
        enabled_set = []
        for entity in used_set:
            if isinstance(entity, NoneEntity):
                pass
            elif isinstance(entity, ContentEntity) or isinstance(entity, IndividualEntity) or isinstance(entity, ListEntity) or isinstance(entity, GroupEntity):
                enabled_set.append(entity)
            else:
                raise TypeError()

        for entity in enabled_set:
            if entity not in disabled_set:
                if isinstance(entity, NoneEntity):
                    pass
                elif isinstance(entity, ContentEntity):
                    yield entity.content
                elif isinstance(entity, IndividualEntity):
                    yield from self.expand(entity.nvmap.values(), disabled_set)
                elif isinstance(entity, ListEntity):
                    yield from self.expand(entity.internal_list, disabled_set)
                elif isinstance(entity, GroupEntity):
                    yield from self.expand(entity.internal_map.values(), disabled_set)
                else:
                    raise TypeError()

    def show(self, body):
        reprs = body.represent(0, '<START>')
        for indent, prefix, ntype, info in reprs:
            print('{}{} {} {}'.format(' ' * indent * 2 + '- ', prefix, ntype, info))

    ## Public Methods for Left Instance(s)

    def create_name_left_subscript(self, name):
        return NameLeftSubscript(name)

    def create_index_left_subscript(self, index):
        return IndexLeftSubscript(index)

    def create_key_left_subscript(self, key):
        return KeyLeftSubscript(key)

    def left_subscript(self, entity, subscript):
        if isinstance(entity, IndividualEntity):
            return LeftIndividualEntitySubscript(entity, subscript)
        elif isinstance(entity, ListEntity):
            return LeftListEntitySubscript(entity, subscript)
        elif isinstance(entity, GroupEntity):
            return LeftGroupEntitySubscript(entity, subscript)
        else:
            raise TypeError()

    ## Public Methods for Filter Trailers

    def create_intermediate_filter_trailer(self, subscript, trailer):
        return IntermediateFilterTrailer(subscript, trailer)

    def create_filter_trailer(self, children, direction, common):
        return FilterTrailer(children, direction, common)

    def create_name_trailer_subscript(self, name):
        return NameTrailerSubscript(name)

    def create_index_trailer_subscript(self, index):
        return IndexTrailerSubscript(index)

    def create_key_trailer_subscript(self, key):
        return KeyTrailerSubscript(key)


class FilterTrailer:
    def __init__(self, children, direction, common):
        self.children = children
        self.direction = direction
        self.common = common

    def apply(self, common, body):
        if self.common is not None:
            common = self.common

        if isinstance(body, GroupEntity):
            internal_map = collections.OrderedDict()
            for key, value in body:
                internal_map[key] = (-1, value)
            for child in self.children:
                indicator, key, value = child.apply(common, body)
                internal_map[key] = (indicator, value)

            entity = GroupEntity()
            for key, (indicator, value) in internal_map.items():
                if indicator * self.direction >= 0:
                    entity.set_by_key(key, value)
            return entity
        elif isinstance(body, ListEntity):
            internal_list = list()
            for index, value in body:
                internal_list.append((-1, value))
            for child in self.children:
                indicator, index, value = child.apply(common, body)
                internal_list[index] = (indicator, value)

            entity = ListEntity()
            for indicator, value in internal_list:
                if indicator * self.direction >= 0:
                    entity.append(value)
                else:
                    entity.append(NoneEntity())
            return entity
        elif isinstance(body, IndividualEntity):
            nvmap = collections.OrderedDict()
            for name, value in body:
                nvmap[name] = (-1, value)
            for child in self.children:
                indicator, name, value = child.apply(None, body)
                nvmap[name] = (indicator, value)

            entity = IndividualEntity()
            for name, (indicator, value) in nvmap.items():
                if indicator * self.direction >= 0:
                    entity.set_by_name(name, value)
            return entity
        else:
            raise TypeError()


class IntermediateFilterTrailer:
    def __init__(self, subscript, trailer):
        self.subscript = subscript
        self.trailer = trailer

    def apply(self, common, body):
        _, subscript, entity = self.subscript.apply(None, body)
        return 0, subscript, self.trailer.apply(common, entity)


class TrailerSubscript:
    def __init__(self):
        pass


class NameTrailerSubscript(TrailerSubscript):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def apply(self, common, body):
        entity = body.get_by_name(self.name)
        if isinstance(entity, IndividualEntity) and common is not None:
            entity = common.apply(None, entity)
        return 1, self.name, entity


class IndexTrailerSubscript(TrailerSubscript):
    def __init__(self, index):
        super().__init__()
        self.index = index

    def apply(self, common, body):
        entity = body.get_by_index(self.index)
        if isinstance(entity, IndividualEntity) and common is not None:
            entity = common.apply(None, entity)
        return 1, self.index, entity


class KeyTrailerSubscript(TrailerSubscript):
    def __init__(self, key):
        super().__init__()
        self.key = key

    def apply(self, common, body):
        entity = body.get_by_key(self.key)
        if isinstance(entity, IndividualEntity) and common is not None:
            entity = common.apply(None, entity)
        return 1, self.key, entity


def count_hex_length(total):
    total -= 1
    count = 0
    while total > 0:
        total //= 16
        count += 1
    return count
