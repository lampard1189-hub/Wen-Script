
import unittest
import subprocess
import sys
import tempfile

from pathlib import Path

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.compiler.semantic import SemanticAnalyzer
from src.compiler.codegen import LLVMCodeGenerator, CodegenError


ROOT = Path(__file__).resolve().parent.parent


class TestWenLexer(unittest.TestCase):

    def test_tokenization(self):
        source = "let age = 20\nprint(age)"
        tokens = Lexer(source).tokenize()

        values = [token.value for token in tokens]

        self.assertIn("let", values)
        self.assertIn("age", values)
        self.assertIn(20, values)
        self.assertIn("print", values)


class TestWenParser(unittest.TestCase):

    def test_control_flow_parsing(self):
        source = """
let age = 20

if age >= 18 {
    print("Adult")
} else {
    print("Under 18")
}

let count = 1

while count <= 5 {
    print(count)
    count = count + 1
}
"""

        tree = Parser(Lexer(source).tokenize()).parse()

        self.assertEqual(len(tree.statements), 4)

        self.assertEqual(
            type(tree.statements[1]).__name__,
            "IfStatement"
        )

        self.assertEqual(
            type(tree.statements[3]).__name__,
            "WhileStatement"
        )


class TestWenSemantic(unittest.TestCase):

    def test_valid_program(self):
        source = """
let number = 10
let result = number + 5
print(result)
"""

        tree = Parser(Lexer(source).tokenize()).parse()

        self.assertTrue(SemanticAnalyzer().analyze(tree))

    def test_undefined_variable(self):
        source = "print(unknown)"

        tree = Parser(Lexer(source).tokenize()).parse()

        with self.assertRaises(Exception):
            SemanticAnalyzer().analyze(tree)


class TestWenCodegen(unittest.TestCase):

    def test_generates_control_flow(self):
        source = """
let count = 1

while count <= 3 {
    print(count)
    count = count + 1
}
"""

        tree = Parser(Lexer(source).tokenize()).parse()

        SemanticAnalyzer().analyze(tree)

        ir = LLVMCodeGenerator().generate(tree)

        self.assertIn("br i1", ir)
        self.assertIn("while.condition", ir)
        self.assertIn("@printf", ir)


class TestWenCompiler(unittest.TestCase):

    def test_native_compilation(self):
        source_file = ROOT / "examples" / "control.wen"

        compilation = subprocess.run(
            [
                sys.executable,
                str(ROOT / "src" / "main.py"),
                str(source_file)
            ],
            cwd=ROOT,
            capture_output=True,
            text=True
        )

        self.assertEqual(
            compilation.returncode,
            0,
            compilation.stderr
        )

        executable = ROOT / "build" / "control"

        execution = subprocess.run(
            [str(executable)],
            capture_output=True,
            text=True
        )

        self.assertEqual(execution.returncode, 0)

        self.assertEqual(
            execution.stdout,
            "Adult\n1\n2\n3\n4\n5\n"
        )



class TestWenDecimal(unittest.TestCase):

    def test_decimal_native_compilation(self):
        source_file = ROOT / "examples" / "decimal.wen"

        compilation = subprocess.run(
            [sys.executable, str(ROOT / "src" / "main.py"),
             str(source_file)],
            cwd=ROOT,
            capture_output=True,
            text=True
        )

        self.assertEqual(compilation.returncode, 0, compilation.stderr)

        executable = ROOT / "build" / "decimal"
        execution = subprocess.run(
            [str(executable)],
            capture_output=True,
            text=True
        )

        self.assertEqual(execution.returncode, 0)
        self.assertEqual(execution.stdout, "14.75\n25\n10.25\n")


class TestWenFunctions(unittest.TestCase):

    def test_function_codegen(self):
        source = """
fn add(a, b) {
    return a + b
}

let result = add(10, 5)
print(result)
"""

        tree = Parser(Lexer(source).tokenize()).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(tree)

        ir = LLVMCodeGenerator().generate(
            tree,
            analyzer.functions,
        )

        self.assertIn(
            "define i64 @wen_fn_add(i64 %arg0, i64 %arg1)",
            ir,
        )
        self.assertIn(
            "@wen_fn_add",
            ir,
        )

    def test_native_function_compilation(self):
        source = """
fn add(a, b) {
    return a + b
}

fn multiply(a, b) {
    return a * b
}

fn identity(value) {
    return value
}

fn get_value() {
    return 20
}

fn get_decimal() {
    return 12.75
}

let result = add(multiply(2, 3), add(1, 2))
let copied = identity(result)
let final_result = add(copied, get_value())
let decimal_result = get_decimal()

print(result)
print(copied)
print(final_result)
print(decimal_result)
"""

        with tempfile.TemporaryDirectory() as temporary:
            source_file = (
                Path(temporary) / "function_regression.wen"
            )

            source_file.write_text(
                source,
                encoding="utf-8",
            )

            compilation = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "src" / "main.py"),
                    str(source_file),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(
                compilation.returncode,
                0,
                compilation.stderr,
            )

            executable = (
                ROOT / "build" / "function_regression"
            )

            try:
                execution = subprocess.run(
                    [str(executable)],
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(
                    execution.returncode,
                    0,
                    execution.stderr,
                )

                self.assertEqual(
                    execution.stdout,
                    "9\n9\n29\n12.75\n",
                )

            finally:
                executable.unlink(missing_ok=True)
                (ROOT / "build" / "function_regression.ll").unlink(
                    missing_ok=True
                )


if __name__ == "__main__":
    unittest.main()

