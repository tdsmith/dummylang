from rply import ParserGenerator, Token  # noqa

from lexer import token_names, lex
import ast

from typing import Union  # noqa

pg = ParserGenerator(
    token_names
)


# Program structure
@pg.production('pgm : head decpart bodypart tail')
def program(p):
    # type: (List) -> ast.Program
    head, decpart, bodypart, tail = p
    assert head.getstr() == tail.getstr()
    return ast.Program(head.getstr(), decpart, bodypart)


@pg.production('head : PROGRAM ID HAS')
def head(p):
    # type: (List[Token]) -> Token
    return p[1]


@pg.production('decpart : DECLS declist')
def decls(p):
    # type: (List) -> ast.IdentifierList
    return p[1]


@pg.production('bodypart : BODY stmtlst')
def bodypart(p):
    # type: (List) -> ast.Block
    return p[1]


@pg.production('tail : END ID')
def tail(p):
    # type: (List) -> Token
    return p[1]


# Declarations
@pg.production('declist : INT varlst')
def declist_int(p):
    # type: (List) -> ast.IdentifierList
    return p[1]


@pg.production('declist : declist INT varlst')
def declist_list(p):
    # type: (List) -> ast.IdentifierList
    return p[0].extend(p[2])


@pg.production('varlst : varlst COMMA ID')
def varlst_varlst(p):
    # type: (List) -> ast.IdentifierList
    return p[0].append_id_token(p[2])


@pg.production('varlst : ID')
def varlst_id(p):
    # type: (List[Token]) -> ast.IdentifierList
    return ast.IdentifierList.from_id_token(p[0])


# Body
@pg.production('stmtlst : stmt')
def stmtlist_stmt(p):
    # type: (List[ast.ASTNode]) -> ast.Block
    return ast.Block.from_statement(p[0])


@pg.production('stmtlst : stmtlst stmt')
def stmtlist_stmtlist(p):
    # type: (List) -> ast.Block
    return p[0].append(p[1])


@pg.production('stmt : WRITE PAREN_L exp PAREN_R')
@pg.production('stmt : WRITELN PAREN_L exp PAREN_R')
def write_statement(p):
    # type: (List) -> ast.WriteStatement
    return ast.WriteStatement(
        p[2],
        newline=True if p[0].gettokentype() == "WRITELN" else False
    )


@pg.production('stmt : READ PAREN_L ID PAREN_R')
def read_statement(p):
    # type: (List[Token]) -> ast.ReadStatement
    assert p[2].gettokentype() == "ID"
    return ast.ReadStatement(ast.IdentifierReference(p[2].getstr()))


@pg.production('stmt : ID ASSIGN exp')
def assign(p):
    # type: (List) -> ast.Assignment
    assert p[0].gettokentype() == "ID"
    return ast.Assignment(ast.IdentifierReference(p[0].getstr()), p[2])


# Expression evaluation
@pg.production('exp : exp PLUS exp')
@pg.production('exp : exp MINUS exp')
def exp_binary_term(p):
    # type: (List[Union[Token, ast.ASTNode]]) -> ast.BinaryOperation
    token_type, left, right = p[1].gettokentype(), p[0], p[2]
    if token_type == "PLUS":
        return ast.Add(left, right)
    elif token_type == "MINUS":
        return ast.Subtract(left, right)
    else:
        raise AssertionError("Shouldn't be here")


@pg.production('exp : NUM')
def factor_num(p):
    # type: (List[Token]) -> ast.Number
    return ast.Number(int(p[0].getstr()))


@pg.production('exp : MINUS NUM')
def factor_negative_num(p):
    # type: (List[Token]) -> ast.Number
    return ast.Number(-int(p[1].getstr()))


@pg.production('exp : ID')
def factor_id(p):
    # type: (List[Token]) -> ast.IdentifierReference
    return ast.IdentifierReference(p[0].getstr())


@pg.production('exp : PAREN_L exp PAREN_R')
def factor_parens(p):
    # type: (List[Union[Token, ast.ASTNode]]) -> ast.ASTNode
    return p[1]


parser = pg.build()

if __name__ == "__main__":
    from pprint import pprint
    from sys import argv
    with open(argv[1], "r") as f:
        p = parser.parse(lex(f.read()))
    pprint(p.__dict__)
    pprint(p.eval({}))
