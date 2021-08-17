class StmtError(Exception):
    def __init__(self, exc_value, node, position):
        super().__init__()
        self.exc_value = exc_value
        self.node = node
        self.position = position

    def __str__(self):
        return 'Line {:d} statement {:d}. {:s}. Exception {:s}, position \'{:s}\'.\n>>> {:s}'.format(self.node.line_index, self.node.stmtcol_index, type(self.node).__name__, type(self.exc_value).__name__, self.position, self.node.content)


class RightExprError(Exception):
    def __init__(self, exc_value, node, position):
        super().__init__()
        self.exc_value = exc_value
        self.node = node
        self.position = position

    def __str__(self):
        return 'Exception {:s}, position \'{:s}\'.'.format(type(self.exc_value).__name__, self.position)


class LeftExprError(Exception):
    def __init__(self, exc_value, node, position):
        super().__init__()
        self.exc_value = exc_value
        self.node = node
        self.position = position

    def __str__(self):
        return 'Exception {:s}, position \'{:s}\'.'.format(type(self.exc_value).__name__, self.position)
