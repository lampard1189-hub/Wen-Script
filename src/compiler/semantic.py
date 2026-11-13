
class SemanticError(Exception):
    pass


class SemanticAnalyzer:

    def __init__(self):
        self.symbols = {}

    def analyze(self, program):
        from src.parser.parser import Program

        if not isinstance(program, Program):
            raise SemanticError("Expected a Program AST.")

        self.symbols = {}
        self.analyze_statements(program.statements)
        return True

    def analyze_statements(self, statements):
        from src.parser.parser import (
            LetStatement,
            AssignmentStatement,
            PrintStatement,
            IfStatement,
            WhileStatement
        )

        for statement in statements:

            if isinstance(statement, LetStatement):
                if statement.name in self.symbols:
                    raise SemanticError(
                        f"Variable '{statement.name}' is already declared."
                    )

                value_type = self.expression_type(statement.value)
                self.symbols[statement.name] = value_type

            elif isinstance(statement, AssignmentStatement):
                if statement.name not in self.symbols:
                    raise SemanticError(
                        f"Undefined variable '{statement.name}'."
                    )

                value_type = self.expression_type(statement.value)
                existing_type = self.symbols[statement.name]

                if value_type != existing_type:
                    raise SemanticError(
                        f"Cannot assign {value_type} to variable "
                        f"'{statement.name}' of type {existing_type}."
                    )

            elif isinstance(statement, PrintStatement):
                self.expression_type(statement.value)

            elif isinstance(statement, IfStatement):
                condition_type = self.expression_type(
                    statement.condition
                )

                if condition_type != "boolean":
                    raise SemanticError(
                        "An if condition must be boolean."
                    )

                self.analyze_block(statement.then_body)

                if statement.else_body is not None:
                    self.analyze_block(statement.else_body)

            elif isinstance(statement, WhileStatement):
                condition_type = self.expression_type(
                    statement.condition
                )

                if condition_type != "boolean":
                    raise SemanticError(
                        "A while condition must be boolean."
                    )

                self.analyze_block(statement.body)

            else:
                raise SemanticError(
                    f"Unsupported statement: "
                    f"{type(statement).__name__}"
                )

    def analyze_block(self, statements):
        previous_symbols = self.symbols.copy()

        try:
            self.analyze_statements(statements)
        finally:
            self.symbols = previous_symbols

    def expression_type(self, expression):
        from src.parser.parser import (
            Number,
            String,
            Boolean,
            Variable,
            Binary,
            Unary
        )

        if isinstance(expression, Number):
            return "decimal" if isinstance(expression.value, float) else "number"

        if isinstance(expression, String):
            return "string"

        if isinstance(expression, Boolean):
            return "boolean"

        if isinstance(expression, Variable):
            if expression.name not in self.symbols:
                raise SemanticError(
                    f"Undefined variable '{expression.name}'."
                )

            return self.symbols[expression.name]

        if isinstance(expression, Unary):
            operand_type = self.expression_type(
                expression.operand
            )

            if expression.operator == "-" and operand_type in {"number", "decimal"}:
                return operand_type

            raise SemanticError(
                "Unary minus requires a number."
            )

        if isinstance(expression, Binary):
            left_type = self.expression_type(expression.left)
            right_type = self.expression_type(expression.right)

            operator = expression.operator

            arithmetic = {"+", "-", "*", "/", "%"}
            comparisons = {"<", ">", "<=", ">="}
            equality = {"==", "!="}

            numeric_types = {"number", "decimal"}

            if operator in arithmetic:
                if left_type not in numeric_types or right_type not in numeric_types:
                    raise SemanticError(
                        f"Operator '{operator}' requires numbers."
                    )

                return "decimal" if "decimal" in {left_type, right_type} else "number"

            if operator in comparisons:
                if left_type not in numeric_types or right_type not in numeric_types:
                    raise SemanticError(
                        f"Comparison '{operator}' requires numbers."
                    )

                return "boolean"

            if operator in equality:
                if left_type != right_type and not (
                    left_type in numeric_types and right_type in numeric_types
                ):
                    raise SemanticError(
                        "Equality comparisons require matching types."
                    )

                return "boolean"

            raise SemanticError(
                f"Unsupported operator '{operator}'."
            )

        raise SemanticError(
            f"Unsupported expression: {type(expression).__name__}"
        )

