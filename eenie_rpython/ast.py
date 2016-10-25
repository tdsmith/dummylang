from rply.token import BaseBox

import os


def raw_input(prompt):
    os.write(1, prompt)
    res = ''
    while True:
        buf = os.read(0, 16)
        if not buf:
            return res
        res += buf
        if res[-1] == '\n':
            return res[:-1]


class ASTNode(BaseBox):
    def eval(self, context):
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
        return Number(self.left.eval(context).getint() +
                      self.right.eval(context).getint())


class Subtract(BinaryOperation):
    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> Number
        return Number(self.left.eval(context).getint() -
                      self.right.eval(context).getint())


class Assignment(ASTNode):
    def __init__(self, identifier, value):
        # type: (IdentifierReference, ASTNode) -> None
        self.identifier = identifier
        self.value = value

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> None
        assert self.identifier.name in context
        context[self.identifier.name] = self.value.eval(context)


class ReadStatement(ASTNode):
    def __init__(self, target):
        # type: (IdentifierReference) -> None
        self.target = target

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> None
        assert self.target.name in context
        context[self.target.name] = (
            Number(int(raw_input("Value for %s: " % self.target.name)))
            .eval(context)
        )


def int_to_bytes(i):
    try:
        _ = b"a" + "a"  # noqa
        return str(i)
    except:
        return str(i).encode("ascii")


class WriteStatement(ASTNode):
    def __init__(self, value, newline=False):
        # type: (IdentifierReference, bool) -> None
        self.value = value
        self.newline = newline

    def eval(self, context):
        # type: (Dict[str, ASTNode]) -> None
        os.write(1, int_to_bytes(self.value.eval(context).getint()) +
                 (b"\n" if self.newline else b""))
