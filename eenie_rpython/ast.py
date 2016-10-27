from rply.token import BaseBox
from typing import Optional  # noqa
import os


class ASTNode(BaseBox):
    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> Optional[ASTNode]
        raise NotImplementedError(self.__class__)


class ASTList(BaseBox):
    def __init__(self, listitems):
        # type: (List[ASTNode]) -> None
        self.listitems = listitems

    def getlist(self):
        # type: () -> List[ASTNode]
        return self.listitems

    def plus(self, other):
        # type: (ASTList) -> ASTList
        assert isinstance(other, ASTList)
        return ASTList(self.listitems + other.listitems)

    def __iter__(self):
        return iter(self.listitems)


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
        self.idname = name

    def get_name(self):
        return self.idname


class IdentifierReference(ASTNode):
    def __init__(self, name):
        # type: (str) -> None
        self.name = name

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> ASTNode
        return context[self.name]


class Program(ASTNode):
    def __init__(self, name, decls, body):
        # type: (str, ASTList, ASTList) -> None
        self.name = name
        self.decls = decls
        self.body = body

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> None
        for identifier in self.decls:
            context[identifier.get_name()] = Number(0)
        for instruction in self.body:
            print(instruction)
            instruction.eval(context)


class BinaryOperation(ASTNode):
    def __init__(self, left, right):
        # type: (ASTNode, ASTNode) -> None
        self.left = left
        self.right = right


class Add(BinaryOperation):
    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> Number
        left = self.left.eval(context)
        right = self.right.eval(context)
        if left is None or right is None:
            raise AssertionError("Attempting to add a non-numeric value")
        return Number(left.getint() + right.getint())


class Subtract(BinaryOperation):
    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> Number
        left = self.left.eval(context)
        right = self.right.eval(context)
        if left is None or right is None:
            raise AssertionError("Attempting to add a null value")
        return Number(left.getint() - right.getint())


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
