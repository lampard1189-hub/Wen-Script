
class CodegenError(Exception):
    pass


class LLVMCodeGenerator:

    def __init__(self):
        self.variables = {}
        self.instructions = []
        self.allocations = []
        self.declaration_slots = {}
        self.string_globals = []
        self.counter = 0
        self.string_counter = 0
        self.label_counter = 0

    def new_temp(self):
        self.counter += 1
        return f"%t{self.counter}"

    def new_label(self, prefix):
        self.label_counter += 1
        return f"{prefix}.{self.label_counter}"

    def emit(self, instruction):
        self.instructions.append("  " + instruction)

    def emit_label(self, label):
        self.instructions.append(f"{label}:")

    def llvm_type(self, value_type):
        return {
            "number": "i64",
            "boolean": "i1",
            "string": "ptr"
        }[value_type]

    def infer_type(self, expression, environment):
        from src.parser.parser import (
            Number, String, Boolean, Variable, Binary, Unary
        )

        if isinstance(expression, Number):
            if not isinstance(expression.value, int):
                raise CodegenError("Only integers are supported.")
            return "number"

        if isinstance(expression, String):
            return "string"

        if isinstance(expression, Boolean):
            return "boolean"

        if isinstance(expression, Variable):
            if expression.name not in environment:
                raise CodegenError(
                    f"Undefined variable '{expression.name}'"
                )
            return environment[expression.name]

        if isinstance(expression, Unary):
            if expression.operator == "-" and (
                self.infer_type(expression.operand, environment) == "number"
            ):
                return "number"
            raise CodegenError("Unsupported unary operation.")

        if isinstance(expression, Binary):
            left_type = self.infer_type(expression.left, environment)
            right_type = self.infer_type(expression.right, environment)

            if left_type != "number" or right_type != "number":
                raise CodegenError(
                    "Binary operations currently require integers."
                )

            if expression.operator in {"+", "-", "*", "/", "%"}:
                return "number"

            if expression.operator in {
                "==", "!=", "<", ">", "<=", ">="
            }:
                return "boolean"

            raise CodegenError(
                f"Unsupported operator '{expression.operator}'"
            )

        raise CodegenError(
            f"Unsupported expression: {type(expression).__name__}"
        )

    def collect_declarations(self, statements, environment):
        from src.parser.parser import (
            LetStatement, IfStatement, WhileStatement
        )

        for statement in statements:

            if isinstance(statement, LetStatement):
                value_type = self.infer_type(
                    statement.value, environment
                )

                slot = f"%v{len(self.declaration_slots) + 1}"

                self.declaration_slots[id(statement)] = (
                    slot, value_type
                )

                self.allocations.append(
                    f"  {slot} = alloca {self.llvm_type(value_type)}"
                )

                environment[statement.name] = value_type

            elif isinstance(statement, IfStatement):
                then_environment = environment.copy()
                self.collect_declarations(
                    statement.then_body, then_environment
                )

                if statement.else_body is not None:
                    else_environment = environment.copy()
                    self.collect_declarations(
                        statement.else_body, else_environment
                    )

            elif isinstance(statement, WhileStatement):
                body_environment = environment.copy()
                self.collect_declarations(
                    statement.body, body_environment
                )

    def generate_expression(self, expression):
        from src.parser.parser import (
            Number, String, Boolean, Variable, Binary, Unary
        )

        if isinstance(expression, Number):
            if not isinstance(expression.value, int):
                raise CodegenError("Only integers are supported.")
            return str(expression.value), "number"

        if isinstance(expression, String):
            name = f"@.str{self.string_counter}"
            self.string_counter += 1

            encoded = expression.value.encode("utf-8")
            escaped = "".join(f"\\{byte:02X}" for byte in encoded)
            length = len(encoded) + 1

            self.string_globals.append(
                f'{name} = private unnamed_addr constant '
                f'[{length} x i8] c"{escaped}\\00"'
            )

            pointer = (
                f"getelementptr inbounds "
                f"([{length} x i8], ptr {name}, i64 0, i64 0)"
            )

            return pointer, "string"

        if isinstance(expression, Boolean):
            return ("1" if expression.value else "0"), "boolean"

        if isinstance(expression, Variable):
            if expression.name not in self.variables:
                raise CodegenError(
                    f"Undefined variable '{expression.name}'"
                )

            slot, value_type = self.variables[expression.name]
            result = self.new_temp()

            self.emit(
                f"{result} = load {self.llvm_type(value_type)}, "
                f"ptr {slot}"
            )

            return result, value_type

        if isinstance(expression, Unary):
            value, value_type = self.generate_expression(
                expression.operand
            )

            if expression.operator == "-" and value_type == "number":
                result = self.new_temp()
                self.emit(f"{result} = sub i64 0, {value}")
                return result, "number"

            raise CodegenError("Unsupported unary operation.")

        if isinstance(expression, Binary):
            left, left_type = self.generate_expression(
                expression.left
            )
            right, right_type = self.generate_expression(
                expression.right
            )

            if left_type != "number" or right_type != "number":
                raise CodegenError(
                    "Binary operations currently require integers."
                )

            operations = {
                "+": ("add", "number"),
                "-": ("sub", "number"),
                "*": ("mul", "number"),
                "/": ("sdiv", "number"),
                "%": ("srem", "number"),
                "==": ("icmp eq", "boolean"),
                "!=": ("icmp ne", "boolean"),
                "<": ("icmp slt", "boolean"),
                ">": ("icmp sgt", "boolean"),
                "<=": ("icmp sle", "boolean"),
                ">=": ("icmp sge", "boolean"),
            }

            if expression.operator not in operations:
                raise CodegenError(
                    f"Unsupported operator '{expression.operator}'"
                )

            operation, result_type = operations[expression.operator]
            result = self.new_temp()

            self.emit(
                f"{result} = {operation} i64 {left}, {right}"
            )

            return result, result_type

        raise CodegenError(
            f"Unsupported expression: {type(expression).__name__}"
        )

    def generate_statements(self, statements):
        from src.parser.parser import (
            LetStatement,
            AssignmentStatement,
            PrintStatement,
            IfStatement,
            WhileStatement
        )

        for statement in statements:

            if isinstance(statement, LetStatement):
                slot, value_type = self.declaration_slots[id(statement)]
                value, actual_type = self.generate_expression(
                    statement.value
                )

                if actual_type != value_type:
                    raise CodegenError("Variable type mismatch.")

                self.emit(
                    f"store {self.llvm_type(value_type)} {value}, "
                    f"ptr {slot}"
                )

                self.variables[statement.name] = (slot, value_type)

            elif isinstance(statement, AssignmentStatement):
                if statement.name not in self.variables:
                    raise CodegenError(
                        f"Undefined variable '{statement.name}'"
                    )

                slot, value_type = self.variables[statement.name]
                value, actual_type = self.generate_expression(
                    statement.value
                )

                if actual_type != value_type:
                    raise CodegenError("Variable type mismatch.")

                self.emit(
                    f"store {self.llvm_type(value_type)} {value}, "
                    f"ptr {slot}"
                )

            elif isinstance(statement, PrintStatement):
                value, value_type = self.generate_expression(
                    statement.value
                )

                if value_type == "string":
                    self.emit(
                        f"call i32 (ptr, ...) @printf("
                        f"ptr @.fmt_str, ptr {value})"
                    )

                else:
                    if value_type == "boolean":
                        converted = self.new_temp()
                        self.emit(
                            f"{converted} = zext i1 {value} to i64"
                        )
                        value = converted

                    self.emit(
                        f"call i32 (ptr, ...) @printf("
                        f"ptr @.fmt_int, i64 {value})"
                    )

            elif isinstance(statement, IfStatement):
                condition, condition_type = self.generate_expression(
                    statement.condition
                )

                if condition_type != "boolean":
                    raise CodegenError(
                        "An if condition must be boolean."
                    )

                then_label = self.new_label("if.then")
                else_label = self.new_label("if.else")
                end_label = self.new_label("if.end")

                self.emit(
                    f"br i1 {condition}, label %{then_label}, "
                    f"label %{else_label}"
                )

                original_variables = self.variables.copy()

                self.emit_label(then_label)
                self.generate_statements(statement.then_body)
                self.emit(f"br label %{end_label}")

                self.variables = original_variables.copy()

                self.emit_label(else_label)

                if statement.else_body is not None:
                    self.generate_statements(statement.else_body)

                self.emit(f"br label %{end_label}")

                self.variables = original_variables.copy()
                self.emit_label(end_label)

            elif isinstance(statement, WhileStatement):
                condition_label = self.new_label("while.condition")
                body_label = self.new_label("while.body")
                end_label = self.new_label("while.end")

                self.emit(f"br label %{condition_label}")

                self.emit_label(condition_label)

                condition, condition_type = self.generate_expression(
                    statement.condition
                )

                if condition_type != "boolean":
                    raise CodegenError(
                        "A while condition must be boolean."
                    )

                self.emit(
                    f"br i1 {condition}, label %{body_label}, "
                    f"label %{end_label}"
                )

                original_variables = self.variables.copy()

                self.emit_label(body_label)
                self.generate_statements(statement.body)
                self.emit(f"br label %{condition_label}")

                self.variables = original_variables.copy()
                self.emit_label(end_label)

            else:
                raise CodegenError(
                    f"Unsupported statement: {type(statement).__name__}"
                )

    def generate(self, program):
        from src.parser.parser import Program

        if not isinstance(program, Program):
            raise CodegenError("Expected a Program AST.")

        self.variables = {}
        self.instructions = []
        self.allocations = []
        self.declaration_slots = {}
        self.string_globals = []
        self.counter = 0
        self.string_counter = 0
        self.label_counter = 0

        self.collect_declarations(program.statements, {})

        self.generate_statements(program.statements)

        globals_text = "\n".join(self.string_globals)
        allocations_text = "\n".join(self.allocations)
        body = "\n".join(self.instructions)

        return f'''source_filename = "wen"

@.fmt_int = private unnamed_addr constant [6 x i8] c"%lld\\0A\\00"
@.fmt_str = private unnamed_addr constant [4 x i8] c"%s\\0A\\00"

{globals_text}

declare i32 @printf(ptr, ...)

define i32 @main() {{
entry:
{allocations_text}
{body}
  ret i32 0
}}
'''

