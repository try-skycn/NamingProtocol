from antlr4 import TerminalNode
from ..grammar import NamingProtocolVisitor
from ..ast import *


__all__ = [
    'CST2AST'
]


class BaseVisitor(NamingProtocolVisitor):
    def visitChildren(self, ctx):
        raise NotImplementedError


class CST2AST(BaseVisitor):
    def __init__(self, input_stream):
        super().__init__()
        self.input_stream = input_stream

    def visitFileInput(self, ctx):
        stmt_converter = StmtConverter(self.input_stream)
        for child in ctx.descendents:
            yield from stmt_converter.visit(child)


class SuiteConverter(BaseVisitor):
    def __init__(self, input_stream):
        super().__init__()
        self.input_stream = input_stream

    def visitSuite(self, ctx):
        stmt_converter = StmtConverter(self.input_stream)
        for child in ctx.descendents:
            yield from stmt_converter.visit(child)


class StmtConverter(BaseVisitor):
    def __init__(self, input_stream):
        super().__init__()
        self.input_stream = input_stream

    def visitSmallStmtLine(self, ctx):
        line_index = ctx.end.line
        for i, child in enumerate(ctx.descendents):
            yield UnitStmtConverter(self.input_stream, line_index - 1, i).visit(child)

    def visitGroupStmtLine(self, ctx):
        yield self.visit(ctx.body)

    def visitScopeStmtLine(self, ctx):
        yield self.visit(ctx.body)

    def visitGroupStmt(self, ctx):
        line_index = ctx.start.line
        return UnitStmtConverter(self.input_stream, line_index, 0).visit(ctx)

    def visitScopeStmt(self, ctx):
        line_index = ctx.start.line
        return UnitStmtConverter(self.input_stream, line_index, 0).visit(ctx)


class UnitStmtConverter(BaseVisitor):
    def __init__(self, input_stream, line_index, stmtcol_index):
        super().__init__()
        self.input_stream = input_stream
        self.line_index = line_index
        self.stmtcol_index = stmtcol_index

    def visitSmallStmt(self, ctx):
        body, = ctx.getChildren()
        return self.visit(body)

    def visitGroupStmt(self, ctx):
        content = self.input_stream.getText(ctx.start.start, ctx.begin.stop)
        return GroupStmtNode(content, self.line_index, self.stmtcol_index, ctx.name.text, list(SuiteConverter(self.input_stream).visit(ctx.body)))

    def visitScopeStmt(self, ctx):
        content = self.input_stream.getText(ctx.start.start, ctx.begin.stop)
        return ScopeStmtNode(content, self.line_index, self.stmtcol_index, ctx.name.text, list(SuiteConverter(self.input_stream).visit(ctx.body)))

    def visitShowStmt(self, ctx):
        content = self.input_stream.getText(ctx.start.start, ctx.stop.stop)
        return ShowStmtNode(content, self.line_index, self.stmtcol_index, None if ctx.body is None else ExprConverter().visit(ctx.body))

    def visitUnzipStmt(self, ctx):
        content = self.input_stream.getText(ctx.start.start, ctx.stop.stop)
        return UnzipStmtNode(content, self.line_index, self.stmtcol_index, ExprConverter().visit(ctx.body))

    def visitUseStmt(self, ctx):
        content = self.input_stream.getText(ctx.start.start, ctx.stop.stop)
        return UseStmtNode(content, self.line_index, self.stmtcol_index, ExprConverter().visit(ctx.body))

    def visitValidateStmt(self, ctx):
        content = self.input_stream.getText(ctx.start.start, ctx.stop.stop)
        return ValidateStmtNode(content, self.line_index, self.stmtcol_index)

    def visitInvalidateStmt(self, ctx):
        content = self.input_stream.getText(ctx.start.start, ctx.stop.stop)
        return InvalidateStmtNode(content, self.line_index, self.stmtcol_index)

    def visitSetStmt(self, ctx):
        content = self.input_stream.getText(ctx.start.start, ctx.stop.stop)
        return SetStmtNode(content, self.line_index, self.stmtcol_index, ExprConverter().visit(ctx.body))

    def visitAssignStmt(self, ctx):
        content = self.input_stream.getText(ctx.start.start, ctx.stop.stop)
        return AssignStmtNode(content, self.line_index, self.stmtcol_index, ExprConverter().visit(ctx.left), ExprConverter().visit(ctx.right))

    def visitCollapseStmt(self, ctx):
        content = self.input_stream.getText(ctx.start.start, ctx.stop.stop)
        keep_chunk_converter = KeepChunkConverter(ExprConverter())
        return CollapseStmtNode(content, self.line_index, self.stmtcol_index, [keep_chunk_converter.visit(child) for child in ctx.descendents])


class ExprConverter(BaseVisitor):
    def __init__(self):
        super().__init__()

    def visitExpr(self, ctx):
        union_chunk_converter = UnionChunkConverter(self)
        if len(ctx.descendents) == 1:
            body, = ctx.descendents
            body, keeps = union_chunk_converter.visit(body)
            assert len(keeps) == 0
            return body
        else:
            pairs = [union_chunk_converter.visit(child) for child in ctx.descendents]
            return UnionExprNode([x for x, _ in pairs], {key: i for i, (_, keys) in enumerate(pairs) for key in keys})

    def visitConcatExpr(self, ctx):
        concat_chunk_converter = ConcatChunkConverter(self)
        left = self.visit(ctx.body)
        for child in ctx.descendents:
            right, connection, choices = concat_chunk_converter.visit(child)
            left = ConcatExprNode(left, right, connection, choices)
        return left

    def visitFilterExpr(self, ctx):
        body = self.visit(ctx.body)
        if ctx.trailer is None:
            return body
        else:
            trailer = FilterTrailerConverter().visit(ctx.trailer)
            return FilterExprNode(body, trailer)

    def visitAtomExpr(self, ctx):
        atom_trailer_converter = AtomTrailerConverter()
        return AtomExprNode(self.visit(ctx.body), [atom_trailer_converter.visit(trailer) for trailer in ctx.trailers])

    def visitSubscriptAtom(self, ctx):
        return SubscriptAtomNode(SubscriptConverter().visit(ctx.body))

    def visitIndivAtom(self, ctx):
        indiv_chunk_converter = IndivChunkConverter(self)
        return IndividualAtomNode([('original', self.visit(ctx.body))] + [indiv_chunk_converter.visit(child) for child in ctx.descendents])

    def visitListAtom(self, ctx):
        return ListAtomNode(integer_converter(ctx.body.text))

    def visitGroupAtom(self, ctx):
        group_chunk_converter = GroupChunkConverter(self)
        return GroupAtomNode([group_chunk_converter.visit(child) for child in ctx.descendents])

    def visitNameAtom(self, ctx):
        return NameAtomNode(ctx.body.text)

    def visitContentAtom(self, ctx):
        return ContentAtomNode(string_converter(ctx.body.text))

    def visitParenAtom(self, ctx):
        return self.visit(ctx.body)


class KeepChunkConverter(BaseVisitor):
    def __init__(self, expr_converter):
        super().__init__()
        self.expr_converter = expr_converter

    def visitKeepChunk(self, ctx):
        return ctx.indicator is not None, self.expr_converter.visit(ctx.body)


class UnionChunkConverter(BaseVisitor):
    def __init__(self, expr_converter):
        super().__init__()
        self.expr_converter = expr_converter

    def visitUnionChunk(self, ctx):
        return self.expr_converter.visit(ctx.body), [string_converter(keep.text) for keep in ctx.keeps]


class ConcatChunkConverter(BaseVisitor):
    def __init__(self, expr_converter):
        super().__init__()
        self.expr_converter = expr_converter

    def visitConcatChunk(self, ctx):
        return self.expr_converter.visit(ctx.body), '_' if ctx.connection is None else string_converter(ctx.connection.text), [self.visit(child) for child in ctx.descendents]

    def visitConcatNameChunk(self, ctx):
        return ctx.name.text, ctx.left.text, ctx.right.text


class FilterTrailerConverter(BaseVisitor):
    def __init__(self):
        super().__init__()

    def visitFilterScript(self, ctx):
        body = SubscriptConverter().visit(ctx.body)
        if ctx.trailer is None:
            trailer = None
        else:
            trailer = SubscriptConverter().visit(ctx.trailer)
        return FilterScriptNode(body, trailer)

    def visitFilterTrailer(self, ctx):
        return FilterTrailerNode([self.visit(child) for child in ctx.descendents], None if ctx.common is None else self.visit(ctx.common), ctx.out is not None)


class AtomTrailerConverter(BaseVisitor):
    def __init__(self):
        super().__init__()

    def visitSubscriptAtomTrailer(self, ctx):
        return SubscriptConverter().visit(ctx.body)

    def visitDotAtomTrailer(self, ctx):
        return NameSubscriptNode(ctx.name.text)


class SubscriptConverter(BaseVisitor):
    def __init__(self):
        super().__init__()

    def visitNameSubscript(self, ctx):
        return NameSubscriptNode(ctx.body.text)

    def visitIntegerSubscript(self, ctx):
        return IntegerSubscriptNode(integer_converter(ctx.body.text))

    def visitStringSubscript(self, ctx):
        return StringSubscriptNode(string_converter(ctx.body.text))


class IndivChunkConverter(BaseVisitor):
    def __init__(self, expr_converter):
        super().__init__()
        self.expr_converter = expr_converter

    def visitIndivChunk(self, ctx):
        return ctx.name.text, self.expr_converter.visit(ctx.value)


class GroupChunkConverter(BaseVisitor):
    def __init__(self, expr_converter):
        super().__init__()
        self.expr_converter = expr_converter

    def visitIndivChunk(self, ctx):
        return string_converter(ctx.key.text), self.expr_converter.visit(ctx.value)


def integer_converter(value):
    return eval(value)


def string_converter(value):
    assert value[0] == value[-1]
    chars = []
    state = '<INIT>'
    for char in value[1:-1]:
        if state == '<INIT>':
            if char == '\\':
                state = '<ESCAPE>'
            else:
                chars.append(char)
        elif state == '<ESCAPE>':
            if char == '\\':
                chars.append('\\')
            elif char == '\'':
                chars.append('\'')
            elif char == '\"':
                chars.append('\"')
            elif char == '`':
                chars.append('`')
            else:
                raise ValueError('Unrecognized escape character: \'{:s}\'.'.format(char))
            state = '<INIT>'
        else:
            raise ValueError()
    return ''.join(chars)
