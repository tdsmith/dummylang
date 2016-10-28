from rply.token import BaseBox, Token  # noqa
from typing import Optional, Iterator  # noqa
import os


class ASTNode(BaseBox):
    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> Optional[ASTNode]
        raise NotImplementedError(self.__class__)


class IdentifierList(BaseBox):
    def __init__(self, identifiers):
        # type: (List[Identifier]) -> None
        self.identifiers = identifiers

    @staticmethod
    def from_id_token(tok):
        # type: (Token) -> IdentifierList
        id = Identifier(tok.getstr())
        return IdentifierList([id])

    def append_id_token(self, tok):
        # type: (Token) -> IdentifierList
        id = Identifier(tok.getstr())
        self.identifiers.append(id)
        return self

    def extend(self, other):
        # type: (IdentifierList) -> IdentifierList
        assert isinstance(other, IdentifierList)
        self.identifiers.extend(other.identifiers)
        return self

    def __iter__(self):
        # type: () -> Iterator[Identifier]
        return iter(self.identifiers)


class Block(ASTNode):
    def __init__(self, statements):
        # type: (List[ASTNode]) -> None
        self.statements = statements

    @staticmethod
    def from_statement(statement):
        # type: (ASTNode) -> Block
        return Block([statement])

    def extend(self, other):
        # type: (Block) -> Block
        assert isinstance(other, Block)
        self.statements.extend(other.statements)
        return self

    def append(self, statement):
        # type: (ASTNode) -> Block
        self.statements.append(statement)
        return self

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> None
        for statement in self.statements:
            statement.eval(context)


class Number(ASTNode):
    def __init__(self, value):
        # type: (int) -> None
        self.intvalue = value

    def getint(self):
        # type: () -> int
        return self.intvalue

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> Number
        return self


class Identifier(ASTNode):
    def __init__(self, name):
        # type: (str) -> None
        self.name = name


class IdentifierReference(ASTNode):
    def __init__(self, name):
        # type: (str) -> None
        self.name = name

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> ASTNode
        return context[self.name]


class Program(ASTNode):
    def __init__(self, name, decls, body):
        # type: (str, IdentifierList, Block) -> None
        self.name = name
        self.decls = decls
        self.body = body

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> None
        for identifier in self.decls:
            context[identifier.name] = Number(0)
        self.body.eval(context)


class BinaryOperation(ASTNode):
    def __init__(self, left, right):
        # type: (ASTNode, ASTNode) -> None
        self.left = left
        self.right = right

    def value_of(self, node, context):
        # type: (ASTNode, Dict[str, ASTNode]) -> Number
        v = node.eval(context)
        if v is None or not isinstance(v, Number):
            raise AssertionError("Expected numeric value: %s" % v)
        return v


class Add(BinaryOperation):
    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> Number
        return Number(self.value_of(self.left, context).getint() +
                      self.value_of(self.right, context).getint())


class Subtract(BinaryOperation):
    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> Number
        return Number(self.value_of(self.left, context).getint() -
                      self.value_of(self.right, context).getint())


class Assignment(ASTNode):
    def __init__(self, identifier, value):
        # type: (IdentifierReference, ASTNode) -> None
        self.identifier = identifier
        self.value = value

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> None
        assert self.identifier.name in context
        value = self.value.eval(context)
        if value is None:
            raise AssertionError("Attempting to assign a null value")
        context[self.identifier.name] = value


class ReadStatement(ASTNode):
    def __init__(self, target):
        # type: (IdentifierReference) -> None
        self.target = target

    @staticmethod
    def raw_input(prompt):
        # type: (bytes) -> bytes
        os.write(1, prompt)
        res = b''
        while True:
            buf = os.read(0, 16)
            if not buf:
                return res
            res += buf
            if res[-1] == '\n':
                return res[:-1]

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> None
        assert self.target.name in context
        context[self.target.name] = (
            Number(int(self.raw_input(b"Value for %s: " % self.target.name)))
            .eval(context)
        )


class WriteStatement(ASTNode):
    def __init__(self, value, newline=False):
        # type: (IdentifierReference, bool) -> None
        self.value = value
        self.newline = newline

    @staticmethod
    def int_to_bytes(i):
        # type: (int) -> bytes
        try:
            _ = b"a" + "a"  # type: ignore # noqa
            return str(i)  # type: ignore
        except:
            return str(i).encode("ascii")

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> None
        os.write(1, self.int_to_bytes(self.value.eval(context).getint()) +
                 (b"\n" if self.newline else b""))
