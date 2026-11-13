
from dataclasses import dataclass

KEYWORDS = {
    "let", "print", "if", "else", "while",
    "true", "false"
}

OPERATORS = {
    "+", "-", "*", "/", "%",
    "=", "==", "!=", "<", ">", "<=", ">="
}


@dataclass
class Token:
    type: str
    value: object
    line: int
    column: int


class Lexer:

    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def advance(self):
        char = self.source[self.position]
        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def peek(self):
        if self.position >= len(self.source):
            return "\0"
        return self.source[self.position]

    def tokenize(self):

        while self.position < len(self.source):

            char = self.peek()

            if char == "\n":
                line, column = self.line, self.column
                self.advance()
                self.tokens.append(
                    Token("NEWLINE", "\n", line, column)
                )
                continue

            if char.isspace():
                self.advance()
                continue

            line = self.line
            column = self.column

            if char == "#":
                while self.peek() not in ("\n", "\0"):
                    self.advance()
                continue

            if char.isalpha() or char == "_":
                value = ""

                while self.peek().isalnum() or self.peek() == "_":
                    value += self.advance()

                token_type = (
                    "KEYWORD" if value in KEYWORDS
                    else "IDENTIFIER"
                )

                if value == "true":
                    token_type, value = "BOOLEAN", True
                elif value == "false":
                    token_type, value = "BOOLEAN", False

                self.tokens.append(
                    Token(token_type, value, line, column)
                )
                continue

            if char.isdigit():
                value = ""

                while self.peek().isdigit():
                    value += self.advance()

                if (self.peek() == "." and
                    self.position + 1 < len(self.source) and
                    self.source[self.position + 1].isdigit()):

                    value += self.advance()

                    while self.peek().isdigit():
                        value += self.advance()

                    number = float(value)
                else:
                    number = int(value)

                self.tokens.append(
                    Token("NUMBER", number, line, column)
                )
                continue

            if char == '"':
                self.advance()
                value = ""

                while self.peek() not in ('"', "\0"):
                    if self.peek() == "\\":
                        self.advance()
                        escaped = self.advance()

                        escapes = {
                            "n": "\n",
                            "t": "\t",
                            '"': '"',
                            "\\": "\\"
                        }

                        if escaped not in escapes:
                            raise SyntaxError(
                                f"Unknown escape at {line}:{column}"
                            )

                        value += escapes[escaped]
                    else:
                        value += self.advance()

                if self.peek() == "\0":
                    raise SyntaxError(
                        f"Unterminated string at {line}:{column}"
                    )

                self.advance()

                self.tokens.append(
                    Token("STRING", value, line, column)
                )
                continue

            two_char = self.source[
                self.position:self.position + 2
            ]

            if two_char in OPERATORS:
                self.advance()
                self.advance()

                self.tokens.append(
                    Token("OPERATOR", two_char, line, column)
                )
                continue

            if char in OPERATORS:
                self.advance()

                self.tokens.append(
                    Token("OPERATOR", char, line, column)
                )
                continue

            if char in "(){}[],;":
                self.advance()

                self.tokens.append(
                    Token("PUNCTUATION", char, line, column)
                )
                continue

            raise SyntaxError(
                f"Unexpected character '{char}' at {line}:{column}"
            )

        self.tokens.append(
            Token("EOF", None, self.line, self.column)
        )

        return self.tokens

