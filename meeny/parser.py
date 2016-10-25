from rply import ParserGenerator

from lexer import token_names, lex
import ast

pg = ParserGenerator(
    token_names,
    precedence=[
        ("left", ["ANGLE_R", "EQUAL", "NOT_EQUAL"]),
        ("left", ["PLUS", "MINUS"]),
        ("left", ["ASTERISK", "DIVIDE", "PERCENT"]),
    ]
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
@pg.production('stmt : WRITELN')
def write_statement(p):
    return ast.WriteStatement(
        p[2] if len(p) > 1 else None,
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


# Control statements
@pg.production('stmt : WHILE exp DO stmtlst ENDWHILE')
def loop(p):
    return ast.WhileStatement(p[1], p[3])


@pg.production('stmt : IF exp THEN stmtlst ELSE stmtlst ENDIF')
def stmt_elif(p):
    return ast.IfStatement(p[1], p[3], p[5])


@pg.production('stmt : IF exp THEN stmtlst ENDIF')
def stmt_if(p):
    return ast.IfStatement(p[1], p[3], None)


# Expression evaluation
@pg.production('exp : exp PLUS exp')
@pg.production('exp : exp MINUS exp')
@pg.production('exp : exp ASTERISK exp')
@pg.production('exp : exp DIVIDE exp')
@pg.production('exp : exp PERCENT exp')
@pg.production('exp : exp EQUAL exp')
@pg.production('exp : exp ANGLE_R exp')
def exp_binary_term(p):
    token_type, left, right = p[1].gettokentype(), p[0], p[2]
    if token_type == "PLUS":
        return ast.Add(left, right)
    elif token_type == "MINUS":
        return ast.Subtract(left, right)
    elif token_type == "ASTERISK":
        return ast.Multiply(left, right)
    elif token_type == "DIVIDE":
        return ast.Divide(left, right)
    elif token_type == "PERCENT":
        return ast.Modulo(left, right)
    elif token_type == "EQUAL":
        return ast.EqualTo(left, right)
    elif token_type == "ANGLE_R":
        return ast.GreaterThan(left, right)
    else:
        assert False, "Shouldn't be here"


@pg.production('exp : NUM')
def factor_num(p):
    return ast.Number(int(p[0].getstr()))


@pg.production('exp : MINUS NUM')
def factor_negative_num(p):
    return ast.Number(-int(p[1].getstr()))


@pg.production('exp : ID')
def factor_id(p):
    return ast.IdentifierReference(p[0].getstr())


@pg.production('exp : PAREN_L exp PAREN_R')
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
