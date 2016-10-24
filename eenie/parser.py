from rply import ParserGenerator

from lexer import token_names, lex
import ast

pg = ParserGenerator(
    token_names
)


# Program structure
@pg.production('pgm : head decpart bodypart tail')
def program(p):
    head, decpart, bodypart, tail = p
    assert head.getstr() == tail.getstr()
    return ast.Program(head.getstr(), decpart, bodypart)


@pg.production('head : PROGRAM ID HAS')
def head(p):
    return p[1]


@pg.production('decpart : DECLS declist')
def decls(p):
    return p[1]


@pg.production('bodypart : BODY stmtlst')
def bodypart(p):
    return p[1]


@pg.production('tail : END ID')
def tail(p):
    return p[1]


# Declarations
@pg.production('declist : INT varlst')
def declist_int(p):
    return p[1]


@pg.production('declist : declist INT varlst')
def declist_list(p):
    return p[0] + p[2]


@pg.production('varlst : varlst COMMA ID')
def varlst_varlst(p):
    return p[0] + [ast.Identifier(p[2].getstr())]


@pg.production('varlst : ID')
def varlst_id(p):
    return [ast.Identifier(p[0].getstr())]


# Body
@pg.production('stmtlst : stmt')
def stmtlist_stmt(p):
    return [p[0]]


@pg.production('stmtlst : stmtlst stmt')
def stmtlist_stmtlist(p):
    return p[0] + [p[1]]


@pg.production('stmt : WRITE PAREN_L exp PAREN_R')
@pg.production('stmt : WRITELN PAREN_L exp PAREN_R')
def write_statement(p):
    return ast.WriteStatement(
        p[2],
        newline=True if p[0].gettokentype() == "WRITELN" else False
    )


@pg.production('stmt : READ PAREN_L ID PAREN_R')
def read_statement(p):
    assert p[2].gettokentype() == "ID"
    return ast.ReadStatement(ast.IdentifierReference(p[2].getstr()))


@pg.production('stmt : ID ASSIGN exp')
def assign(p):
    assert p[0].gettokentype() == "ID"
    return ast.Assignment(ast.IdentifierReference(p[0].getstr()), p[2])


# Expression evaluation
@pg.production('exp : term')
def exp_term(p):
    return p[0]


@pg.production('exp : exp PLUS term')
@pg.production('exp : exp MINUS term')
def exp_binary_term(p):
    token_type, left, right = p[1].gettokentype(), p[0], p[2]
    if token_type == "PLUS":
        return ast.Add(left, right)
    elif token_type == "MINUS":
        return ast.Subtract(left, right)
    else:
        assert False, "Shouldn't be here"


@pg.production('term : factor')
def exp_factor(p):
    return p[0]


@pg.production('factor : NUM')
def factor_num(p):
    return ast.Number(int(p[0].getstr()))


@pg.production('factor : MINUS NUM')
def factor_negative_num(p):
    return ast.Number(-int(p[1].getstr()))


@pg.production('factor : ID')
def factor_id(p):
    return ast.IdentifierReference(p[0].getstr())


@pg.production('factor : PAREN_L exp PAREN_R')
def factor_parens(p):
    return p[1]


parser = pg.build()

if __name__ == "__main__":
    from pprint import pprint
    from sys import argv
    with open(argv[1], "r") as f:
        p = parser.parse(lex(f.read()))
    pprint(p.__dict__)
    pprint(p.eval({}))
