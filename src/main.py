
import argparse
import shutil
import subprocess
import sys

from pathlib import Path

# Locate the Wen project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.compiler.semantic import SemanticAnalyzer
from src.compiler.codegen import LLVMCodeGenerator


def compile_wen(source_file):

    source_file = Path(source_file).resolve()

    if not source_file.is_file():
        raise FileNotFoundError(
            f"Source file not found: {source_file}"
        )

    # Locate LLVM Clang
    clang = Path("/opt/homebrew/opt/llvm/bin/clang")

    if not clang.is_file():
        clang = shutil.which("clang")

    if not clang:
        raise RuntimeError("LLVM Clang was not found.")

    # Read Wen source
    source = source_file.read_text(encoding="utf-8")

    # Stage 1: Lexical analysis
    tokens = Lexer(source).tokenize()

    # Stage 2: Parsing
    tree = Parser(tokens).parse()

    # Stage 3: Semantic analysis
    SemanticAnalyzer().analyze(tree)

    # Stage 4: LLVM code generation
    llvm_ir = LLVMCodeGenerator().generate(tree)

    # Prepare build directory
    build_dir = PROJECT_DIR / "build"
    build_dir.mkdir(exist_ok=True)

    ir_file = build_dir / f"{source_file.stem}.ll"
    executable = build_dir / source_file.stem

    # Save LLVM IR
    ir_file.write_text(llvm_ir, encoding="utf-8")

    # Stage 5: Native compilation
    subprocess.run(
        [
            str(clang),
            "-Wno-override-module",
            str(ir_file),
            "-o",
            str(executable),
        ],
        check=True,
    )

    print("\nWen compilation successful!")
    print(f"LLVM IR: {ir_file}")
    print(f"Executable: {executable}")


def main():

    parser = argparse.ArgumentParser(
        description="Wen Programming Language Compiler"
    )

    parser.add_argument(
        "source",
        help="Wen source file (.wen)"
    )

    args = parser.parse_args()

    try:
        compile_wen(args.source)

    except Exception as error:
        print(f"\nWen compilation failed: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

