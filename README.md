# Wen Programming Language

**Wen** is an experimental, Python-inspired programming language that compiles source code into native executables using LLVM.

Wen explores programming-language design, compiler construction, semantic analysis, and native code generation.

**Current release:** `0.2.0a1`
**Development status:** Experimental alpha

## Key Features

- Python-inspired syntax
- Variable declarations using `let`
- Integer, decimal, string, and boolean values
- Arithmetic and comparison operators
- Output using `print()`
- Conditional statements using `if` and `else`
- Loops using `while`
- User-defined functions using `fn`
- Function parameters and return values
- Nested and zero-argument function calls
- Decimal function return values
- Variable assignment
- Semantic analysis
- LLVM intermediate representation (IR) generation
- Native executable compilation

## How Wen Works

Wen uses a compiler pipeline to transform source code into a native executable.

```text
Wen Source Code
       |
       v
     Lexer
       |
       v
     Parser
       |
       v
Semantic Analysis
       |
       v
LLVM Code Generation
       |
       v
    LLVM IR
       |
       v
 Native Compilation
       |
       v
Executable Program
```

## Requirements

- Python 3.10 or later
- Clang compiler
- A supported development environment

## Installation

The published PyPI package is an experimental alpha release:

```bash
python3 -m pip install wen-lang==0.2.0a1
```

**Note:** The latest function-development work may be ahead of the published PyPI release. Use the development installation below to access the current development branch.

## Getting Started

Create a file named `hello.wen`:

```wen
let message = "Hello from Wen!"
print(message)
```

Run it from the project source:

```bash
python3 src/main.py hello.wen
```

## Variables and Expressions

Wen supports variable declarations and arithmetic expressions.

```wen
let first = 10
let second = 5
let result = first + second

print(result)
```

## Control Flow

Wen supports conditional statements and `while` loops.

```wen
let count = 1

while count <= 5 {
    print(count)
    count = count + 1
}
```

## Functions

Wen supports user-defined functions using the `fn` keyword, with parameters and return values.

### Function example

```wen
fn add(a, b) {
    return a + b
}

fn multiply(a, b) {
    return a * b
}

let result = add(10, multiply(2, 3))
print(result)
```

### Function capabilities

- User-defined functions
- Function parameters and return values
- Nested function calls
- Zero-argument function calls
- Integer and decimal function return values

### Current limitations

- Function parameters currently support integer values.
- Return statements must be the final top-level statement in a function.
- Return statements inside conditional statements and loops are not yet supported.

## Development Installation

Clone the development branch:

```bash
git clone -b development/v0.2 https://github.com/lampard1189-hub/Wen-Script.git
cd Wen-Script
```

Run Wen directly from the source:

```bash
python3 src/main.py examples/hello.wen
```

## Running Tests

Run the test suite:

```bash
python3 -m unittest discover -s tests -v
```

## Project Structure

```text
Wen-Script/
|
|-- src/
|   |-- lexer/
|   |-- parser/
|   |-- compiler/
|   |-- runtime/
|
|-- examples/
|-- tests/
|-- docs/
|-- README.md
|-- pyproject.toml
```

## Development Roadmap

- Decimal function parameters
- Return statements inside conditional statements and loops
- Improved compiler diagnostics
- User-defined types
- Additional target architectures
- Expanded standard library
- More advanced memory management

## Project Links

- **GitHub Repository:** https://github.com/lampard1189-hub/Wen-Script
- **Documentation:** https://lampard1189-hub.github.io/Wen-Script/docs/
- **Project Website:** https://lampard1189-hub.github.io/Wen-Script/
- **PyPI:** https://pypi.org/project/wen-lang/

## License

## License

See the `LICENSE` file for licensing information.
