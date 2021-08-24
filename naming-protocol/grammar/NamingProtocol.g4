grammar NamingProtocol;

import Python3;

/*
 * parser rules
 */

// Start Symbols

fileInput: (NEWLINE | descendents+=stmtLine)* EOF;

// Statements

suite: NEWLINE INDENT descendents+=stmtLine* DEDENT;
stmtLine
    : descendents+=smallStmt (SEMI descendents+=smallStmt)* SEMI? end=NEWLINE #smallStmtLine
    | body=groupStmt end=NEWLINE #groupStmtLine
    | body=scopeStmt end=NEWLINE #scopeStmtLine
    ;
smallStmt: showStmt | unzipStmt | useStmt | validateStmt | invalidateStmt | setStmt | assignStmt | collapseStmt;
groupStmt: (setIndicator='set' key=STRING?)? 'group' name=NAME begin='begin' body=suite 'end';
scopeStmt: 'scope' name=NAME begin='begin' body=suite 'end';
showStmt: 'show' body=expr;
unzipStmt: 'unzip' body=expr;
useStmt: 'use' body=expr;
validateStmt: 'validate';
invalidateStmt: 'invalidate';
setStmt: 'set' body=expr;
assignStmt: left=expr '=' right=expr;
collapseStmt: 'collapse' descendents+=keepChunk (',' descendents+=keepChunk)*;
keepChunk: indicator='keep'? body=expr;

// Expressions

expr: descendents+=unionChunk ('|' descendents+=unionChunk)*;
unionChunk: body=concatExpr ('[' 'keep' keeps+=STRING (',' keeps+=STRING)* ']')?;
concatExpr: body=filterExpr ('+' descendents+=concatChunk)*;
concatChunk: body=filterExpr ('@' reverse='reverse'? connection=STRING)? descendents+=concatNameChunk*;
concatNameChunk: '@' name=NAME '=' left=NAME '*' right=NAME;
filterExpr: body=atomExpr trailer=filterTrailer?;
filterScript: body=subscript trailer=filterTrailer?;
filterTrailer: '{' (descendents+=filterScript (',' descendents+=filterScript)*)? (';' common=filterTrailer)? '}' out='~'?;
atomExpr: body=atom trailers+=atomTrailer*;
atom: '[' body=subscript ']' #subscriptAtom
    | '<' body=expr (',' descendents+=indivChunk)* '>' #indivAtom
    | '<' body=INTEGER '>' #listAtom
    | '{' descendents+=groupChunk (',' descendents+=groupChunk)* '}' #groupAtom
    | body=NAME #nameAtom
    | body=STRING #contentAtom
    | '(' body=expr ')' #parenAtom
    ;
indivChunk: name=NAME '=' value=expr;
groupChunk: key=STRING ':' value=expr;
atomTrailer
    : '[' body=subscript ']' #subscriptAtomTrailer
    | '.' name=NAME #dotAtomTrailer
    ;
subscript
    : body=NAME #nameSubscript
    | body=INTEGER #integerSubscript
    | body=STRING #stringSubscript
    ;

/*
 * lexer rules
 */

// Keywords

GROUP:              'group';
SCOPE:              'scope';
UNZIP:              'unzip';
USE:                'use';
VALIDATE:           'validate';
INVALIDATE:         'invalidate';
SET:                'set';
BIND:               'bind';
COLLAPSE:           'collapse';
SHOW:               'show';
BEGIN:              'begin';
END:                'end';
REVERSE:            'reverse';

// Separators

LPAREN:             '(' {self.opened += 1};
RPAREN:             ')' {self.opened -= 1};
LBRACE:             '{' {self.opened += 1};
RBRACE:             '}' {self.opened -= 1};
LBRACK:             '[' {self.opened += 1};
RBRACK:             ']' {self.opened -= 1};
LCHEVRON:           '<' {self.opened += 1};
RCHEVRON:           '>' {self.opened -= 1};
COMMA:              ',';
SEMI:               ';';
CONCATOP:           '+';
CHOICEOP:           '*';
OROP:               '|';
ASSIGNOP:           '=';
NEGOP:              '~';
DOTOP:              '.';
ATOP:               '@';
COLLAPSEOP:         '<-';

// Literals

STRING
 : STRING_LITERAL
 ;

STRING_LITERAL
 : SHORT_STRING
 ;

/*
 * fragments
 */

fragment SHORT_STRING
 : '\'' ( STRING_ESCAPE_SEQ | ~[\\\r\n\f'] )* '\''
 | '"' ( STRING_ESCAPE_SEQ | ~[\\\r\n\f"] )* '"'
 | '`' ( STRING_ESCAPE_SEQ | ~[\\\r\n\f`] )* '`'
 ;

fragment STRING_ESCAPE_SEQ
 : '\\' .
 ;
