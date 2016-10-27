from collections import OrderedDict
from rply import LexerGenerator, Token
from typing import Callable, Iterator  # noqa

reserved = ["program", "has", "decls", "int", "body", "end", "read",
            "write", "writeln"]

operators = OrderedDict([
    ("COMMA", ","),
    ("PAREN_L", r"\("),
    ("PAREN_R", r"\)"),
    ("ASSIGN", "<-"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
])

lg = LexerGenerator()

lg.add("NUM", r"\d+")
lg.add("ID", r"[a-zA-Z][a-zA-Z0-9]*")

for key, value in operators.items():
    lg.add(key, value)


def id_reserved(token):
    if token.value.lower() in reserved:
        return Token(token.value.upper(), token.value)
    return token


callbacks = {
    "ID": [id_reserved],
}  # type: Dict[str, List[Callable[[Token], Token]]]

lg.ignore(r"\s+")
lg.ignore(r"^#.*")
lexer = lg.build()

token_names = [rule.name for rule in lg.rules] + [name.upper() for name in reserved]


def lex(buf):
    # type: (bytes) -> Iterator[Token]
    for token in lexer.lex(buf):
        for callback in callbacks.get(token.name, []):
            token = callback(token)
        yield token
