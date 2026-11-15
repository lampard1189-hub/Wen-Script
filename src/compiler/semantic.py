
class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.symbols = {}
        self.functions = {}
        self.current_function = None
        self.return_type = None

    def analyze(self, program):
        from src.parser.parser import Program, FunctionDefinition

        if not isinstance(program, Program):
            raise SemanticError("Expected a Program AST.")

        self.symbols = {}
        self.functions = {}

        # Register function names and parameter counts first.
        for statement in program.statements:
            if isinstance(statement, FunctionDefinition):
                if statement.name in self.functions:
                    raise SemanticError(
                        f"Function '{statement.name}' is already defined."
                    )

                self.functions[statement.name] = {
                    "parameters": statement.parameters,
                    "return_type": None
                }

        # Analyse function bodies.
        for statement in program.statements:
            if isinstance(statement, FunctionDefinition):
                self.analyze_function(statement)

        # Analyse ordinary top-level statements.
        main_statements = [
            statement for statement in program.statements
            if not isinstance(statement, FunctionDefinition)
        ]

        self.current_function = None
        self.return_type = None
        self.symbols = {}
        self.analyze_statements(main_statements)

        return True

    def analyze_function(self, function):
        from src.parser.parser import ReturnStatement

        self.current_function = function.name
        self.return_type = None
        self.symbols = {}

        for parameter in function.parameters:
            if parameter in self.symbols:
                raise SemanticError(
                    f"Duplicate parameter '{parameter}'."
                )

            self.symbols[parameter] = "number"

        self.analyze_statements(function.body)

        if self.return_type is None:
            raise SemanticError(
                f"Function '{function.name}' must return a value."
            )

        self.functions[function.name]["return_type"] = self.return_type

        self.current_function = None
        self.return_type = None
        self.symbols = {}

    def analyze_statements(self, statements):
        from src.parser.parser import (
            LetStatement,
            AssignmentStatement,
            PrintStatement,
            IfStatement,
            WhileStatement,
            ReturnStatement,
            FunctionDefinition
        )

        for statement in statements:

            if isinstance(statement, FunctionDefinition):
                if self.current_function is not None:
                    raise SemanticError(
                        "Functions cannot be defined inside other functions."
                    )

            elif isinstance(statement, LetStatement):
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

            elif isinstance(statement, ReturnStatement):
                if self.current_function is None:
                    raise SemanticError(
                        "Return statements must be inside a function."
                    )

                value_type = self.expression_type(statement.value)

                if value_type not in {"number", "decimal"}:
                    raise SemanticError(
                        "Functions must return a number or decimal."
                    )

                if self.return_type is not None:
                    if self.return_type != value_type:
                        raise SemanticError(
                            "A function must use a consistent return type."
                        )

                self.return_type = value_type

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
            Unary,
            FunctionCall
        )

        if isinstance(expression, Number):
            return (
                "decimal"
                if isinstance(expression.value, float)
                else "number"
            )

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

        if isinstance(expression, FunctionCall):
            if expression.name not in self.functions:
                raise SemanticError(
                    f"Undefined function '{expression.name}'."
                )

            function = self.functions[expression.name]
            parameters = function["parameters"]

            if len(expression.arguments) != len(parameters):
                raise SemanticError(
                    f"Function '{expression.name}' expects "
                    f"{len(parameters)} arguments, but received "
                    f"{len(expression.arguments)}."
                )

            for argument in expression.arguments:
                argument_type = self.expression_type(argument)

                if argument_type not in {"number", "decimal"}:
                    raise SemanticError(
                        "Function arguments must be numeric."
                    )

            return function["return_type"] or "number"

        if isinstance(expression, Unary):
            operand_type = self.expression_type(
                expression.operand
            )

            if expression.operator == "-" and operand_type in {
                "number", "decimal"
            }:
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
                if (
                    left_type not in numeric_types
                    or right_type not in numeric_types
                ):
                    raise SemanticError(
                        f"Operator '{operator}' requires numbers."
                    )

                return (
                    "decimal"
                    if "decimal" in {left_type, right_type}
                    else "number"
                )

            if operator in comparisons:
                if (
                    left_type not in numeric_types
                    or right_type not in numeric_types
                ):
                    raise SemanticError(
                        f"Comparison '{operator}' requires numbers."
                    )

                return "boolean"

            if operator in equality:
                if left_type != right_type and not (
                    left_type in numeric_types
                    and right_type in numeric_types
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

