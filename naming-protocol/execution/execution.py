from ..error import *
from ..ast import ASTVisitor


__all__ = [
    'ExecutionModel'
]


class ExecutionModel(ASTVisitor):
    def __init__(self, model, initial_context):
        super().__init__()
        self.model = model
        self.context = initial_context
        self.printed = False

    def prepare_printing(self):
        if self.printed:
            print()
        else:
            self.printed = True

    def visitGroupStmtNode(self, node):
        try:
            group_builder = self.context.push_group_builder(node.name)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'push')

        for i, child in enumerate(node.children):
            try:
                self.visit(child)
            except Exception as exc_value:
                raise StmtError(exc_value, node, 'children[{:d}]'.format(i))

        try:
            self.context.pop()
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'pop')

        try:
            self.context.set_by_name(group_builder.name, group_builder.build())
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'set')

    def visitScopeStmtNode(self, node):
        try:
            scope_processor = self.context.push_scope_processor(node.name)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'push')

        for i, child in enumerate(node.children):
            try:
                self.visit(child)
            except Exception as exc_value:
                raise StmtError(exc_value, node, 'children[{:d}]'.format(i))

        try:
            self.context.pop()
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'pop')

    def visitShowStmtNode(self, node):
        try:
            body = RightExprModel(self.model, self.context).visit(node.body)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'body')

        self.prepare_printing()
        print('Line {:d}, statement {:d}: {:s}'.format(node.line_index, node.stmtcol_index, node.content))
        self.model.show(body)

    def visitUnzipStmtNode(self, node):
        try:
            assert self.context.is_group_builder() or self.context.is_scope_processor()
        except AssertionError as exc_value:
            raise StmtError(exc_value, node, 'assertion')

        environment = self.context.top()

        try:
            body = RightExprModel(self.model, self.context).visit(node.body)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'body')

        try:
            environment.unzip(body)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'unzip')

    def visitUseStmtNode(self, node):
        try:
            assert self.context.is_scope_processor()
        except AssertionError as exc_value:
            raise StmtError(exc_value, node, 'assertion')

        scope_processor = self.context.top()

        try:
            body = RightExprModel(self.model, self.context).visit(node.body)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'body')

        try:
            scope_processor.use(body)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'use')

    def visitValidateStmtNode(self, node):
        try:
            assert self.context.is_scope_processor()
        except AssertionError as exc_value:
            raise StmtError(exc_value, node, 'assertion')

        scope_processor = self.context.top()

        self.prepare_printing()
        print('Line {:d}, statement {:d}: {:s}'.format(node.line_index, node.stmtcol_index, node.content))
        try:
            scope_processor.validate(self.model)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'validate')

    def visitInvalidateStmtNode(self, node):
        try:
            assert self.context.is_scope_processor()
        except AssertionError as exc_value:
            raise StmtError(exc_value, node, 'assertion')

        scope_processor = self.context.top()

        self.prepare_printing()
        print('Line {:d}, statement {:d}: {:s}'.format(node.line_index, node.stmtcol_index, node.content))
        try:
            scope_processor.invalidate(self.model)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'invalidate')

    def visitSetStmtNode(self, node):
        try:
            assert self.context.is_group_builder() or self.context.is_scope_processor()
        except AssertionError as exc_value:
            raise StmtError(exc_value, node, 'assertion')

        try:
            body = RightExprModel(self.model, self.context).visit(node.body)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'body')

        try:
            self.context.set_entity(body)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'set')

    def visitAssignStmtNode(self, node):
        try:
            left = LeftExprModel(self.model, self.context).visit(node.left)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'left')

        try:
            right = RightExprModel(self.model, self.context).visit(node.right)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'right')

        try:
            left.set(right)
        except Exception as exc_value:
            raise StmtError(exc_value, node, 'set')

    def visitCollapseStmtNode(self, node):
        left_expr_model = LeftExprModel(self.model, self.context)
        for i, (indicator, child) in enumerate(node.pairs):
            try:
                left_expr = left_expr_model.visit(child)
            except Exception as exc_value:
                raise StmtError(exc_value, node, 'pairs[{:d}]'.format(i))

            if not indicator:
                left_expr.set(self.model.create_none_entity())


class LeftExprModel(ASTVisitor):
    def __init__(self, model, context):
        super().__init__()
        self.model = model
        self.context = context

    def visitAtomExprNode(self, node):
        if len(node.trailers) == 0:
            try:
                body = self.visit(node.body)
            except Exception as exc_value:
                raise LeftExprError(exc_value, node, 'length-0-body')

            return body
        else:
            try:
                body = RightExprModel(self.model, self.context).visit(node.body)
            except Exception as exc_value:
                raise LeftExprError(exc_value, node, 'length-pos-body')

            *head, tail = node.trailers
            for i, trailer in enumerate(head):
                try:
                    body = RightSubscriptModel(body).visit(trailer)
                except Exception as exc_value:
                    raise LeftExprError(exc_value, node, 'length-pos-trailers[{:s}]'.format(i))

            try:
                subscript = LeftSubscriptModel(self.model).visit(tail)
            except Exception as exc_value:
                raise LeftExprError(exc_value, node, 'length-pos-tail')

            try:
                expr = self.model.left_subscript(body, subscript)
            except Exception as exc_value:
                raise LeftExprError(exc_value, node, 'length-pos-expression')

            return expr

    def visitSubscriptAtomNode(self, node):
        try:
            subscript = LeftSubscriptModel(self.model).visit(node.subscript)
        except Exception as exc_value:
            raise LeftExprError(exc_value, node, 'subscript')

        try:
            expr = self.context.left_subscript(subscript)
        except Exception as exc_value:
            raise LeftExprError(exc_value, node, 'expression')

        return expr

    def visitNameAtomNode(self, node):
        try:
            subscript = self.model.create_name_left_subscript(node.name)
        except Exception as exc_value:
            raise LeftExprError(exc_value, node, 'subscript')

        try:
            expr = self.context.left_subscript(subscript)
        except Exception as exc_value:
            raise LeftExprError(exc_value, node, 'expression')

        return expr


class LeftSubscriptModel(ASTVisitor):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def visitNameSubscriptNode(self, node):
        return self.model.create_name_left_subscript(node.name)

    def visitIntegerSubscriptNode(self, node):
        return self.model.create_index_left_subscript(node.index)

    def visitStringSubscriptNode(self, node):
        return self.model.create_key_left_subscript(node.key)


class RightExprModel(ASTVisitor):
    def __init__(self, model, context):
        super().__init__()
        self.model = model
        self.context = context

    def visitUnionExprNode(self, node):
        children = []
        for i, child in enumerate(node.children):
            try:
                child = self.visit(child)
            except Exception as exc_value:
                raise RightExprError(exc_value, node, 'children[{:d}]'.format(i))

            children.append(child)

        try:
            expr = self.model.group_union(children, node.keeps)
        except Exception as exc_value:
            raise RightExprError(exc_value, node, 'expression')

        return expr

    def visitConcatExprNode(self, node):
        try:
            left = self.visit(node.left)
        except Exception as exc_value:
            raise RightExprError(exc_value, node, 'left')

        try:
            right = self.visit(node.right)
        except Exception as exc_value:
            raise RightExprError(exc_value, node, 'right')

        try:
            expr = self.model.cross(left, right, node.connection, node.choices)
        except Exception as exc_value:
            raise RightExprError(exc_value, node, 'expression')

        return expr

    def visitFilterExprNode(self, node):
        try:
            body = self.visit(node.body)
        except Exception as exc_value:
            raise RightExprError(exc_value, node, 'body')

        if node.trailer is None:
            return body
        else:
            try:
                filter_trailer = FilterTrailerModel(self.model).visit(node.trailer)
            except Exception as exc_value:
                raise RightExprError(exc_value, node, 'filter-trailer')

            try:
                expr = self.model.group_filter(body, filter_trailer)
            except Exception as exc_value:
                raise RightExprError(exc_value, node, 'expression')

            return expr

    def visitAtomExprNode(self, node):
        try:
            body = self.visit(node.body)
        except Exception as exc_value:
            raise RightExprError(exc_value, node, 'body')

        for i, trailer in enumerate(node.trailers):
            try:
                body = RightSubscriptModel(body).visit(trailer)
            except Exception as exc_value:
                raise RightExprError(exc_value, node, 'trailers[{:s}]'.format(i))

        return body

    def visitSubscriptAtomNode(self, node):
        try:
            expr = SubscriptAtomModel(self.context).visit(node.subscript)
        except Exception as exc_value:
            raise RightExprError(exc_value, node, 'expression')

        return expr

    def visitIndividualAtomNode(self, node):
        pairs = []
        for name, value in node.pairs:
            try:
                value = self.visit(value)
            except Exception as exc_value:
                raise RightExprError(exc_value, node, 'pairs[{:s}]'.format(name))

            pairs.append((name, value))

        try:
            expr = self.model.create_individual_entity(pairs)
        except Exception as exc_value:
            raise RightExprError(exc_value, node, 'expression')

        return expr

    def visitListAtomNode(self, node):
        try:
            expr = self.model.create_list_entity(node.length)
        except Exception as exc_value:
            raise RightExprError(exc_value, node, 'expression')

        return expr

    def visitGroupAtomNode(self, node):
        pairs = []
        for name, value in node.pairs:
            try:
                value = self.visit(value)
            except Exception as exc_value:
                raise RightExprError(exc_value, node, 'pairs[{:s}]'.format(name))

            pairs.append((name, value))

        try:
            expr = self.model.create_group_entity(pairs)
        except Exception as exc_value:
            raise RightExprError(exc_value, node, 'expression')

        return expr

    def visitNameAtomNode(self, node):
        try:
            expr = self.context.get_by_name(node.name)
        except Exception as exc_value:
            raise RightExprError(exc_value, node, 'expression')

        return expr

    def visitContentAtomNode(self, node):
        return self.model.create_content_entity(node.content)


class RightSubscriptModel(ASTVisitor):
    def __init__(self, entity):
        super().__init__()
        self.entity = entity

    def visitNameSubscriptNode(self, node):
        return self.entity.get_by_name(node.name)

    def visitIntegerSubscriptNode(self, node):
        return self.entity.get_by_index(node.index)

    def visitStringSubscriptNode(self, node):
        return self.entity.get_by_key(node.key)


class FilterTrailerModel(ASTVisitor):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def visitFilterScriptNode(self, node):
        subscript = FilterSubscriptModel(self.model).visit(node.body)
        if node.trailer is None:
            return subscript
        else:
            trailer = self.visit(node.trailer)
            return self.model.create_intermediate_filter_trailer(subscript, trailer)

    def visitFilterTrailerNode(self, node):
        children = [self.visit(child) for child in node.children]
        direction = -1 if node.out else 1
        common = None if node.common is None else self.visit(node.common)
        return self.model.create_filter_trailer(children, direction, common)


class SubscriptAtomModel(ASTVisitor):
    def __init__(self, context):
        super().__init__()
        self.context = context

    def visitNameSubscriptNode(self, node):
        return self.context.get_by_name(node.name)

    def visitIntegerSubscriptNode(self, node):
        return self.context.get_by_index(node.index)

    def visitStringSubscriptNode(self, node):
        return self.context.get_by_key(node.key)


class FilterSubscriptModel(ASTVisitor):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def visitNameSubscriptNode(self, node):
        return self.model.create_name_trailer_subscript(node.name)

    def visitIntegerSubscriptNode(self, node):
        return self.model.create_index_trailer_subscript(node.index)

    def visitStringSubscriptNode(self, node):
        return self.model.create_key_trailer_subscript(node.key)
