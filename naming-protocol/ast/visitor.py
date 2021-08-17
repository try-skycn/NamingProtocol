__all__ = [
    'ASTVisitor'
]


class ASTVisitor:
    def __init__(self):
        pass

    def visit(self, node):
        return node.accept(self)

    def visitASTNode(self, node):
        raise NotImplementedError

    def visitStmtNode(self, node):
        return self.visitASTNode(node)

    def visitGroupStmtNode(self, node):
        return self.visitStmtNode(node)

    def visitScopeStmtNode(self, node):
        return self.visitStmtNode(node)

    def visitShowStmtNode(self, node):
        return self.visitStmtNode(node)

    def visitUnzipStmtNode(self, node):
        return self.visitStmtNode(node)

    def visitUseStmtNode(self, node):
        return self.visitStmtNode(node)

    def visitValidateStmtNode(self, node):
        return self.visitStmtNode(node)

    def visitInvalidateStmtNode(self, node):
        return self.visitStmtNode(node)

    def visitSetStmtNode(self, node):
        return self.visitStmtNode(node)

    def visitAssignStmtNode(self, node):
        return self.visitStmtNode(node)

    def visitCollapseStmtNode(self, node):
        return self.visitStmtNode(node)

    def visitExprNode(self, node):
        return self.visitASTNode(node)

    def visitUnionExprNode(self, node):
        return self.visitExprNode(node)

    def visitConcatExprNode(self, node):
        return self.visitExprNode(node)

    def visitFilterExprNode(self, node):
        return self.visitExprNode(node)

    def visitFilterScriptNode(self, node):
        return self.visitASTNode(node)

    def visitFilterTrailerNode(self, node):
        return self.visitASTNode(node)

    def visitAtomExprNode(self, node):
        return self.visitExprNode(node)

    def visitAtomNode(self, node):
        return self.visitExprNode(node)

    def visitSubscriptAtomNode(self, node):
        return self.visitAtomNode(node)

    def visitIndividualAtomNode(self, node):
        return self.visitAtomNode(node)

    def visitListAtomNode(self, node):
        return self.visitAtomNode(node)

    def visitGroupAtomNode(self, node):
        return self.visitAtomNode(node)

    def visitNameAtomNode(self, node):
        return self.visitAtomNode(node)

    def visitContentAtomNode(self, node):
        return self.visitAtomNode(node)

    def visitSubscriptNode(self, node):
        return self.visitASTNode(node)

    def visitNameSubscriptNode(self, node):
        return self.visitSubscriptNode(node)

    def visitIntegerSubscriptNode(self, node):
        return self.visitSubscriptNode(node)

    def visitStringSubscriptNode(self, node):
        return self.visitSubscriptNode(node)
