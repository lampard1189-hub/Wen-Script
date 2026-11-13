from dataclasses import dataclass


# ABSTRACT SYNTAX TREE

@dataclass
class Number:
    value: object


@dataclass
class String:
    value: str


@dataclass
class Boolean:
    value: bool


@dataclass
class Variable:
    name: str


@dataclass
class Binary:
    left: object
    operator: str
    right: object


@dataclass
class Unary:
    operator: str
    operand: object


@dataclass
class LetStatement:
    name: str
    value: object


@dataclass
class AssignmentStatement:
    name: str
    value: object


@dataclass
class PrintStatement:
    value: object


@dataclass
class IfStatement:
    condition: object
    then_body: list
    else_body: list


@dataclass
class WhileStatement:
    condition: object
    body: list


@dataclass
class Program:
    statements: list


# PARSER

class Parser:

    PRECEDENCE = {
        "==": 1,
        "!=": 1,
        "<": 1,
        ">": 1,
        "<=": 1,
        ">=": 1,
        "+": 2,
        "-": 2,
        "*": 3,
        "/": 3,
        "%": 3,
    }

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        return self.tokens[self.position]

    def advance(self):
        token = self.current()
        if token.type != "EOF":
            self.position += 1
        return token

    def peek(self):
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return self.tokens[-1]

    def match(self, token_type, value=None):
        token = self.current()
        if token.type == token_type:
            if value is None or token.value == value:
                self.advance()
                return True
        return False

    def expect(self, token_type, value=None):
        token = self.current()
        if not self.match(token_type, value):
            raise SyntaxError(
                f"Expected {value or token_type} "
                f"at line {token.line}, column {token.column}"
            )
        return token

    def skip_separators(self):
        while (
            self.match("NEWLINE")
            or self.match("PUNCTUATION", ";")
        ):
            pass

    def parse(self):
        statements = []
        self.skip_separators()

        while self.current().type != "EOF":
            statements.append(self.statement())
            self.skip_separators()

        return Program(statements)

    def block(self):
        self.expect("PUNCTUATION", "{")
        statements = []
        self.skip_separators()

        while not (
            self.current().type == "PUNCTUATION"
            and self.current().value == "}"
        ):
            if self.current().type == "EOF":
                raise SyntaxError("Expected closing '}'")

            statements.append(self.statement())
            self.skip_separators()

        self.expect("PUNCTUATION", "}")
        return statements

    def statement(self):

        if self.match("KEYWORD", "let"):
            name = self.expect("IDENTIFIER").value
            self.expect("OPERATOR", "=")
            value = self.expression()
            return LetStatement(name, value)

        if self.match("KEYWORD", "print"):
            if self.match("PUNCTUATION", "("):
                value = self.expression()
                self.expect("PUNCTUATION", ")")
            else:
                value = self.expression()

            return PrintStatement(value)

        if self.match("KEYWORD", "if"):
            condition = self.expression()
            then_body = self.block()
            else_body = []

            self.skip_separators()

            if self.match("KEYWORD", "else"):
                else_body = self.block()

            return IfStatement(
                condition, then_body, else_body
            )

        if self.match("KEYWORD", "while"):
            condition = self.expression()
            body = self.block()
            return WhileStatement(condition, body)

        if (
            self.current().type == "IDENTIFIER"
            and self.peek().type == "OPERATOR"
            and self.peek().value == "="
        ):
            name = self.advance().value
            self.expect("OPERATOR", "=")
            value = self.expression()
            return AssignmentStatement(name, value)

        token = self.current()
        raise SyntaxError(
            f"Unexpected statement at "
            f"{token.line}:{token.column}"
        )

    def expression(self, min_precedence=0):
        left = self.primary()

        while self.current().type == "OPERATOR":
            operator = self.current().value
            precedence = self.PRECEDENCE.get(operator, -1)

            if precedence < min_precedence:
                break

            self.advance()
            right = self.expression(precedence + 1)
            left = Binary(left, operator, right)

        return left

    def primary(self):
        token = self.current()

        if self.match("NUMBER"):
            return Number(token.value)

        if self.match("STRING"):
            return String(token.value)

        if self.match("BOOLEAN"):
            return Boolean(token.value)

        if self.match("IDENTIFIER"):
            return Variable(token.value)

        if self.match("OPERATOR", "-"):
            return Unary("-", self.expression(4))

        if self.match("PUNCTUATION", "("):
            value = self.expression()
            self.expect("PUNCTUATION", ")")
            return value

        raise SyntaxError(
            f"Unexpected expression at "
            f"{token.line}:{token.column}"
        )

