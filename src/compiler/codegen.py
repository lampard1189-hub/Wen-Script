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

        self.functions = {}
        self.current_return_type = None

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
        types = {
            "number": "i64",
            "decimal": "double",
            "boolean": "i1",
            "string": "ptr",
        }

        if value_type not in types:
            raise CodegenError(
                f"Unsupported Wen type '{value_type}'."
            )

        return types[value_type]

    def infer_type(self, expression, environment):
        from src.parser.parser import (
            Number,
            String,
            Boolean,
            Variable,
            Binary,
            Unary,
            FunctionCall,
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
            if expression.name not in environment:
                raise CodegenError(
                    f"Undefined variable '{expression.name}'"
                )

            return environment[expression.name]

        if isinstance(expression, Unary):
            operand_type = self.infer_type(
                expression.operand,
                environment,
            )

            if (
                expression.operator == "-"
                and operand_type in {"number", "decimal"}
            ):
                return operand_type

            raise CodegenError("Unsupported unary operation.")

        if isinstance(expression, FunctionCall):
            if expression.name not in self.functions:
                raise CodegenError(
                    f"Undefined function '{expression.name}'"
                )

            signature = self.functions[expression.name]
            parameters = signature["parameters"]

            if len(expression.arguments) != len(parameters):
                raise CodegenError(
                    f"Function '{expression.name}' expects "
                    f"{len(parameters)} arguments, but received "
                    f"{len(expression.arguments)}."
                )

            for argument in expression.arguments:
                argument_type = self.infer_type(
                    argument,
                    environment,
                )

                if argument_type != "number":
                    raise CodegenError(
                        "Function arguments must currently be "
                        "whole numbers."
                    )

            return signature["return_type"]

        if isinstance(expression, Binary):
            left_type = self.infer_type(
                expression.left,
                environment,
            )

            right_type = self.infer_type(
                expression.right,
                environment,
            )

            numeric_types = {"number", "decimal"}

            if (
                left_type not in numeric_types
                or right_type not in numeric_types
            ):
                raise CodegenError(
                    "Binary operations require numbers."
                )

            if expression.operator in {"+", "-", "*", "/", "%"}:
                return (
                    "decimal"
                    if "decimal" in {left_type, right_type}
                    else "number"
                )

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
            LetStatement,
            IfStatement,
            WhileStatement,
        )

        for statement in statements:

            if isinstance(statement, LetStatement):
                if statement.name in environment:
                    raise CodegenError(
                        f"Variable '{statement.name}' is already declared."
                    )

                value_type = self.infer_type(
                    statement.value,
                    environment,
                )

                slot = f"%v{len(self.declaration_slots) + 1}"

                self.declaration_slots[id(statement)] = (
                    slot,
                    value_type,
                )

                self.allocations.append(
                    f"  {slot} = alloca {self.llvm_type(value_type)}"
                )

                environment[statement.name] = value_type

            elif isinstance(statement, IfStatement):
                then_environment = environment.copy()

                self.collect_declarations(
                    statement.then_body,
                    then_environment,
                )

                if statement.else_body is not None:
                    else_environment = environment.copy()

                    self.collect_declarations(
                        statement.else_body,
                        else_environment,
                    )

            elif isinstance(statement, WhileStatement):
                body_environment = environment.copy()

                self.collect_declarations(
                    statement.body,
                    body_environment,
                )

    def generate_expression(self, expression):
        from src.parser.parser import (
            Number,
            String,
            Boolean,
            Variable,
            Binary,
            Unary,
            FunctionCall,
        )

        if isinstance(expression, Number):
            value_type = (
                "decimal"
                if isinstance(expression.value, float)
                else "number"
            )

            return repr(expression.value), value_type

        if isinstance(expression, String):
            name = f"@.str{self.string_counter}"
            self.string_counter += 1

            encoded = expression.value.encode("utf-8")

            escaped = "".join(
                f"\\{byte:02X}"
                for byte in encoded
            )

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
            return (
                "1" if expression.value else "0"
            ), "boolean"

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

        if isinstance(expression, FunctionCall):
            if expression.name not in self.functions:
                raise CodegenError(
                    f"Undefined function '{expression.name}'"
                )

            signature = self.functions[expression.name]
            parameters = signature["parameters"]

            if len(expression.arguments) != len(parameters):
                raise CodegenError(
                    f"Function '{expression.name}' expects "
                    f"{len(parameters)} arguments, but received "
                    f"{len(expression.arguments)}."
                )

            arguments = []

            for argument in expression.arguments:
                value, value_type = self.generate_expression(
                    argument
                )

                if value_type != "number":
                    raise CodegenError(
                        "Function arguments must currently be "
                        "whole numbers."
                    )

                arguments.append(f"i64 {value}")

            return_type = signature["return_type"]
            result = self.new_temp()

            argument_text = ", ".join(arguments)

            self.emit(
                f"{result} = call {self.llvm_type(return_type)} "
                f"@wen_fn_{expression.name}({argument_text})"
            )

            return result, return_type

        if isinstance(expression, Unary):
            value, value_type = self.generate_expression(
                expression.operand
            )

            if (
                expression.operator == "-"
                and value_type in {"number", "decimal"}
            ):
                result = self.new_temp()

                if value_type == "decimal":
                    self.emit(
                        f"{result} = fneg double {value}"
                    )
                else:
                    self.emit(
                        f"{result} = sub i64 0, {value}"
                    )

                return result, value_type

            raise CodegenError("Unsupported unary operation.")

        if isinstance(expression, Binary):
            left, left_type = self.generate_expression(
                expression.left
            )

            right, right_type = self.generate_expression(
                expression.right
            )

            numeric_types = {"number", "decimal"}

            if (
                left_type not in numeric_types
                or right_type not in numeric_types
            ):
                raise CodegenError(
                    "Binary operations require numbers."
                )

            use_decimal = (
                "decimal" in {left_type, right_type}
            )

            llvm_numeric_type = (
                "double" if use_decimal else "i64"
            )

            if use_decimal:
                if left_type == "number":
                    converted = self.new_temp()

                    self.emit(
                        f"{converted} = sitofp i64 {left} to double"
                    )

                    left = converted

                if right_type == "number":
                    converted = self.new_temp()

                    self.emit(
                        f"{converted} = sitofp i64 {right} to double"
                    )

                    right = converted

            operator = expression.operator

            arithmetic_ops = {
                "+": "fadd" if use_decimal else "add",
                "-": "fsub" if use_decimal else "sub",
                "*": "fmul" if use_decimal else "mul",
                "/": "fdiv" if use_decimal else "sdiv",
                "%": "frem" if use_decimal else "srem",
            }

            comparison_ops = {
                "==": "oeq" if use_decimal else "eq",
                "!=": "one" if use_decimal else "ne",
                "<": "olt" if use_decimal else "slt",
                ">": "ogt" if use_decimal else "sgt",
                "<=": "ole" if use_decimal else "sle",
                ">=": "oge" if use_decimal else "sge",
            }

            result = self.new_temp()

            if operator in arithmetic_ops:
                operation = arithmetic_ops[operator]

                result_type = (
                    "decimal" if use_decimal else "number"
                )

                self.emit(
                    f"{result} = {operation} "
                    f"{llvm_numeric_type} {left}, {right}"
                )

                return result, result_type

            if operator in comparison_ops:
                predicate = comparison_ops[operator]

                instruction = (
                    "fcmp" if use_decimal else "icmp"
                )

                self.emit(
                    f"{result} = {instruction} "
                    f"{predicate} {llvm_numeric_type} "
                    f"{left}, {right}"
                )

                return result, "boolean"

            raise CodegenError(
                f"Unsupported operator '{operator}'"
            )

        raise CodegenError(
            f"Unsupported expression: {type(expression).__name__}"
        )

    def generate_statements(self, statements):
        from src.parser.parser import (
            LetStatement,
            AssignmentStatement,
            PrintStatement,
            IfStatement,
            WhileStatement,
            ReturnStatement,
        )

        for statement in statements:

            if isinstance(statement, LetStatement):
                slot, value_type = self.declaration_slots[
                    id(statement)
                ]

                value, actual_type = self.generate_expression(
                    statement.value
                )

                if actual_type != value_type:
                    raise CodegenError(
                        "Variable type mismatch."
                    )

                self.emit(
                    f"store {self.llvm_type(value_type)} {value}, "
                    f"ptr {slot}"
                )

                self.variables[statement.name] = (
                    slot,
                    value_type,
                )

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
                    raise CodegenError(
                        "Variable type mismatch."
                    )

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

                elif value_type == "decimal":
                    self.emit(
                        f"call i32 (ptr, ...) @printf("
                        f"ptr @.fmt_float, double {value})"
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

            elif isinstance(statement, ReturnStatement):
                if self.current_return_type is None:
                    raise CodegenError(
                        "Return statements are only allowed "
                        "inside functions."
                    )

                value, actual_type = self.generate_expression(
                    statement.value
                )

                if actual_type != self.current_return_type:
                    raise CodegenError(
                        "Function return type mismatch."
                    )

                self.emit(
                    f"ret {self.llvm_type(actual_type)} {value}"
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

                self.emit(
                    f"br label %{end_label}"
                )

                self.variables = original_variables.copy()

                self.emit_label(else_label)

                if statement.else_body is not None:
                    self.generate_statements(
                        statement.else_body
                    )

                self.emit(
                    f"br label %{end_label}"
                )

                self.variables = original_variables.copy()

                self.emit_label(end_label)

            elif isinstance(statement, WhileStatement):
                condition_label = self.new_label(
                    "while.condition"
                )

                body_label = self.new_label("while.body")
                end_label = self.new_label("while.end")

                self.emit(
                    f"br label %{condition_label}"
                )

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

                self.emit(
                    f"br label %{condition_label}"
                )

                self.variables = original_variables.copy()

                self.emit_label(end_label)

            else:
                raise CodegenError(
                    f"Unsupported statement: "
                    f"{type(statement).__name__}"
                )

    def contains_return(self, statements):
        from src.parser.parser import (
            ReturnStatement,
            IfStatement,
            WhileStatement,
        )

        for statement in statements:
            if isinstance(statement, ReturnStatement):
                return True

            if isinstance(statement, IfStatement):
                if self.contains_return(statement.then_body):
                    return True

                if (
                    statement.else_body is not None
                    and self.contains_return(statement.else_body)
                ):
                    return True

            if isinstance(statement, WhileStatement):
                if self.contains_return(statement.body):
                    return True

        return False

    def validate_function_body(self, function):
        from src.parser.parser import (
            ReturnStatement,
            IfStatement,
            WhileStatement,
        )

        body = function.body

        if not body:
            raise CodegenError(
                f"Function '{function.name}' has an empty body."
            )

        for statement in body:
            if isinstance(statement, (IfStatement, WhileStatement)):
                if self.contains_return([statement]):
                    raise CodegenError(
                        "Returns inside if and while blocks "
                        "are not supported yet."
                    )

        return_statements = [
            statement
            for statement in body
            if isinstance(statement, ReturnStatement)
        ]

        if len(return_statements) != 1:
            raise CodegenError(
                f"Function '{function.name}' must have "
                "exactly one direct return statement."
            )

        if not isinstance(body[-1], ReturnStatement):
            raise CodegenError(
                f"Function '{function.name}' must end "
                "with a return statement."
            )

    def reset_function_state(self):
        self.variables = {}
        self.instructions = []
        self.allocations = []
        self.declaration_slots = {}

        self.current_return_type = None

    def generate_function(self, function):
        self.validate_function_body(function)

        signature = self.functions[function.name]
        parameters = signature["parameters"]
        return_type = signature["return_type"]

        if return_type not in {"number", "decimal"}:
            raise CodegenError(
                f"Unsupported return type for '{function.name}'."
            )

        self.reset_function_state()
        self.current_return_type = return_type

        llvm_parameters = []
        parameter_stores = []

        for index, parameter in enumerate(parameters):
            slot = f"%p{index + 1}"
            argument = f"%arg{index}"

            llvm_parameters.append(
                f"i64 {argument}"
            )

            self.allocations.append(
                f"  {slot} = alloca i64"
            )

            parameter_stores.append(
                f"  store i64 {argument}, ptr {slot}"
            )

            self.variables[parameter] = (
                slot,
                "number",
            )

        parameter_environment = {
            name: "number"
            for name in parameters
        }

        self.collect_declarations(
            function.body,
            parameter_environment,
        )

        self.generate_statements(function.body)

        allocation_text = "\n".join(self.allocations)
        store_text = "\n".join(parameter_stores)
        body_text = "\n".join(self.instructions)

        parameters_text = ", ".join(llvm_parameters)

        return f'''define {self.llvm_type(return_type)} @wen_fn_{function.name}({parameters_text}) {{
entry:
{allocation_text}
{store_text}
{body_text}
}}
'''

    def generate(self, program, functions=None):
        from src.parser.parser import (
            Program,
            FunctionDefinition,
        )

        if not isinstance(program, Program):
            raise CodegenError(
                "Expected a Program AST."
            )

        self.variables = {}
        self.instructions = []
        self.allocations = []
        self.declaration_slots = {}
        self.string_globals = []

        self.counter = 0
        self.string_counter = 0
        self.label_counter = 0

        self.functions = functions or {}

        function_definitions = [
            statement
            for statement in program.statements
            if isinstance(statement, FunctionDefinition)
        ]

        for function in function_definitions:
            if function.name not in self.functions:
                raise CodegenError(
                    f"Missing semantic information for "
                    f"function '{function.name}'."
                )

        function_text = []

        for function in function_definitions:
            function_text.append(
                self.generate_function(function)
            )

        self.reset_function_state()

        self.current_return_type = None

        main_statements = [
            statement
            for statement in program.statements
            if not isinstance(statement, FunctionDefinition)
        ]

        self.collect_declarations(
            main_statements,
            {},
        )

        self.generate_statements(main_statements)

        globals_text = "\n".join(self.string_globals)
        allocations_text = "\n".join(self.allocations)
        body_text = "\n".join(self.instructions)

        functions_text = "\n".join(function_text)

        return f'''source_filename = "wen"

@.fmt_int = private unnamed_addr constant [6 x i8] c"%lld\\0A\\00"
@.fmt_str = private unnamed_addr constant [4 x i8] c"%s\\0A\\00"
@.fmt_float = private unnamed_addr constant [4 x i8] c"%g\\0A\\00"

{globals_text}

declare i32 @printf(ptr, ...)

{functions_text}

define i32 @main() {{
entry:
{allocations_text}
{body_text}
  ret i32 0
}}
'''
