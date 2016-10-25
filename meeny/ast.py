import sys

import attr


try:
    raw_input
except NameError:
    raw_input = input


class ASTNode(object):
    def eval(self, context):
        raise NotImplementedError(self.__class__)


@attr.s
class Number(ASTNode):
    value = attr.ib(convert=int)

    def eval(self, context):
        return self.value


@attr.s
class Identifier(ASTNode):
    name = attr.ib(validator=attr.validators.instance_of(str))
    value = attr.ib(default=None)


@attr.s
class IdentifierReference(ASTNode):
    name = attr.ib(validator=attr.validators.instance_of(str))

    def eval(self, context):
        return context[self.name]


def is_list_of_identifiers(instance, attribute, value):
    for v in value:
        attr.validators.instance_of(Identifier)(instance, attribute, v)


@attr.s
class Program(ASTNode):
    name = attr.ib()
    decls = attr.ib(validator=is_list_of_identifiers)
    body = attr.ib()

    def eval(self, context):
        for identifier in self.decls:
            context[identifier.name] = identifier.value
        for instruction in self.body:
            print(instruction)
            instruction.eval(context)
        for identifier in self.decls:
            if context[identifier.name] is None:
                print("Warning: identifier %s not used." % identifier.name)


@attr.s
class BinaryOperation(ASTNode):
    left = attr.ib(validator=attr.validators.instance_of(ASTNode))
    right = attr.ib(validator=attr.validators.instance_of(ASTNode))


class Add(BinaryOperation):
    def eval(self, context):
        return self.left.eval(context) + self.right.eval(context)


class Subtract(BinaryOperation):
    def eval(self, context):
        return self.left.eval(context) - self.right.eval(context)


class Multiply(BinaryOperation):
    def eval(self, context):
        return self.left.eval(context) * self.right.eval(context)


class Divide(BinaryOperation):
    def eval(self, context):
        return self.left.eval(context) // self.right.eval(context)


class Modulo(BinaryOperation):
    def eval(self, context):
        return self.left.eval(context) % self.right.eval(context)


class GreaterThan(BinaryOperation):
    def eval(self, context):
        return self.left.eval(context) > self.right.eval(context)


class EqualTo(BinaryOperation):
    def eval(self, context):
        return self.left.eval(context) == self.right.eval(context)


@attr.s
class Assignment(ASTNode):
    identifier = attr.ib(validator=attr.validators.instance_of(IdentifierReference))
    value = attr.ib(validator=attr.validators.instance_of(ASTNode))

    def eval(self, context):
        assert self.identifier.name in context
        context[self.identifier.name] = self.value.eval(context)


@attr.s
class ReadStatement(ASTNode):
    target = attr.ib(validator=attr.validators.instance_of(IdentifierReference))

    def eval(self, context):
        assert self.target.name in context
        context[self.target.name] = (
            Number(raw_input("Value for %s: " % self.target.name))
            .eval(context)
        )


@attr.s
class WriteStatement(ASTNode):
    value = attr.ib(validator=attr.validators.optional(
        attr.validators.instance_of(ASTNode)
    ))
    newline = attr.ib(default=False)

    def eval(self, context):
        val = str(self.value.eval(context)) if self.value else ""
        sys.stdout.write(val + ("\n" if self.newline else ""))


@attr.s
class WhileStatement(ASTNode):
    condition = attr.ib(validator=attr.validators.instance_of(ASTNode))
    body = attr.ib()

    def eval(self, context):
        while self.condition.eval(context):
            for statement in self.body:
                statement.eval(context)


@attr.s
class IfStatement(ASTNode):
    condition = attr.ib(validator=attr.validators.instance_of(ASTNode))
    body = attr.ib()
    else_body = attr.ib()

    def eval(self, context):
        if self.condition.eval(context):
            for statement in self.body:
                statement.eval(context)
        elif self.else_body:
            for statement in self.else_body:
                statement.eval(context)
