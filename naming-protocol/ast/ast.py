class ASTNode:
    def __init__(self):
        pass

    def accept(self, visitor):
        return visitor.visitASTNode(self)


class StmtNode(ASTNode):
    def __init__(self, content, line_index, stmtcol_index):
        """
        stmtcol = statement column
        """
        super().__init__()
        self.content = content
        self.line_index = line_index
        self.stmtcol_index = stmtcol_index

    def accept(self, visitor):
        return visitor.visitStmtNode(self)


class GroupStmtNode(StmtNode):
    def __init__(self, content, line_index, stmtcol_index, name, children):
        super().__init__(content, line_index, stmtcol_index)
        self.name = name
        self.children = children

    def accept(self, visitor):
        return visitor.visitGroupStmtNode(self)


class ScopeStmtNode(StmtNode):
    def __init__(self, content, line_index, stmtcol_index, name, children):
        super().__init__(content, line_index, stmtcol_index)
        self.name = name
        self.children = children

    def accept(self, visitor):
        return visitor.visitScopeStmtNode(self)


class ShowStmtNode(StmtNode):
    def __init__(self, content, line_index, stmtcol_index, body):
        super().__init__(content, line_index, stmtcol_index)
        self.body = body

    def accept(self, visitor):
        return visitor.visitShowStmtNode(self)


class UnzipStmtNode(StmtNode):
    def __init__(self, content, line_index, stmtcol_index, body):
        super().__init__(content, line_index, stmtcol_index)
        self.body = body

    def accept(self, visitor):
        return visitor.visitUnzipStmtNode(self)


class UseStmtNode(StmtNode):
    def __init__(self, content, line_index, stmtcol_index, body):
        super().__init__(content, line_index, stmtcol_index)
        self.body = body

    def accept(self, visitor):
        return visitor.visitUseStmtNode(self)


class ValidateStmtNode(StmtNode):
    def __init__(self, content, line_index, stmtcol_index):
        super().__init__(content, line_index, stmtcol_index)

    def accept(self, visitor):
        return visitor.visitValidateStmtNode(self)


class InvalidateStmtNode(StmtNode):
    def __init__(self, content, line_index, stmtcol_index):
        super().__init__(content, line_index, stmtcol_index)

    def accept(self, visitor):
        return visitor.visitInvalidateStmtNode(self)


class SetStmtNode(StmtNode):
    def __init__(self, content, line_index, stmtcol_index, body):
        super().__init__(content, line_index, stmtcol_index)
        self.body = body

    def accept(self, visitor):
        return visitor.visitSetStmtNode(self)


class AssignStmtNode(StmtNode):
    def __init__(self, content, line_index, stmtcol_index, left, right):
        super().__init__(content, line_index, stmtcol_index)
        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visitAssignStmtNode(self)


class CollapseStmtNode(StmtNode):
    def __init__(self, content, line_index, stmtcol_index, pairs):
        super().__init__(content, line_index, stmtcol_index)
        self.pairs = pairs

    def accept(self, visitor):
        return visitor.visitCollapseStmtNode(self)


class ExprNode(ASTNode):
    def __init__(self):
        super().__init__()

    def accept(self, visitor):
        return visitor.visitExprNode(self)


class UnionExprNode(ExprNode):
    def __init__(self, children, keeps):
        super().__init__()
        self.children = children
        self.keeps = keeps

    def accept(self, visitor):
        return visitor.visitUnionExprNode(self)


class ConcatExprNode(ExprNode):
    def __init__(self, left, right, connection, choices):
        super().__init__()
        self.left = left
        self.right = right
        self.connection = connection
        self.choices = choices

    def accept(self, visitor):
        return visitor.visitConcatExprNode(self)


class FilterExprNode(ExprNode):
    def __init__(self, body, trailer):
        super().__init__()
        self.body = body
        self.trailer = trailer

    def accept(self, visitor):
        return visitor.visitFilterExprNode(self)


class FilterScriptNode(ASTNode):
    def __init__(self, body, trailer):
        super().__init__()
        self.body = body
        self.trailer = trailer

    def accept(self, visitor):
        return visitor.visitFilterScriptNode(self)


class FilterTrailerNode(ASTNode):
    def __init__(self, children, common, out):
        super().__init__()
        self.children = children
        self.common = common
        self.out = out

    def accept(self, visitor):
        return visitor.visitFilterTrailerNode(self)


class AtomExprNode(ExprNode):
    def __init__(self, body, trailers):
        super().__init__()
        self.body = body
        self.trailers = trailers

    def accept(self, visitor):
        return visitor.visitAtomExprNode(self)


class AtomNode(ExprNode):
    def __init__(self):
        super().__init__()

    def accept(self, visitor):
        return visitor.visitAtomNode(self)


class SubscriptAtomNode(AtomNode):
    def __init__(self, subscript):
        super().__init__()
        self.subscript = subscript

    def accept(self, visitor):
        return visitor.visitSubscriptAtomNode(self)


class IndividualAtomNode(AtomNode):
    def __init__(self, pairs):
        super().__init__()
        self.pairs = pairs

    def accept(self, visitor):
        return visitor.visitIndividualAtomNode(self)


class ListAtomNode(AtomNode):
    def __init__(self, length):
        super().__init__()
        self.length = length

    def accept(self, visitor):
        return visitor.visitListAtomNode(self)


class GroupAtomNode(AtomNode):
    def __init__(self, pairs):
        super().__init__()
        self.pairs = pairs

    def accept(self, visitor):
        return visitor.visitGroupAtomNode(self)


class NameAtomNode(AtomNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def accept(self, visitor):
        return visitor.visitNameAtomNode(self)


class ContentAtomNode(AtomNode):
    def __init__(self, content):
        super().__init__()
        self.content = content

    def accept(self, visitor):
        return visitor.visitContentAtomNode(self)


class SubscriptNode(ASTNode):
    def __init__(self):
        super().__init__()

    def accept(self, visitor):
        return visitor.visitSubscriptNode(self)


class NameSubscriptNode(SubscriptNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def accept(self, visitor):
        return visitor.visitNameSubscriptNode(self)


class IntegerSubscriptNode(SubscriptNode):
    def __init__(self, index):
        super().__init__()
        self.index = index

    def accept(self, visitor):
        return visitor.visitIntegerSubscriptNode(self)


class StringSubscriptNode(SubscriptNode):
    def __init__(self, key):
        super().__init__()
        self.key = key

    def accept(self, visitor):
        return visitor.visitStringSubscriptNode(self)
