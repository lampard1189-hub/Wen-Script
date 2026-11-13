
import unittest
import subprocess
import sys

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


if __name__ == "__main__":
    unittest.main()

