# Learn Wen

Welcome to Wen! Wen is an experimental, Python-inspired programming language that uses an LLVM-based compiler to turn source code into native executables.

This guide introduces the language, demonstrates its syntax, and explains how its compiler works.

## 1. What is Wen?

Wen is a programming language project designed to explore language implementation, compiler architecture, semantic analysis, and native code generation.

Its development focuses on:

- Readable, Python-inspired syntax
- Variables and expressions
- Conditional statements and loops
- User-defined functions
- Semantic analysis
- LLVM intermediate representation
- Native executable compilation

Wen is experimental. Its syntax and implementation may change as development continues.

## 2. Getting Started

### Requirements

- Python 3.10 or later
- Clang compiler
- A supported development environment

### Get the source code

Clone the development branch:

```bash
git clone -b development/v0.2 https://github.com/lampard1189-hub/Wen-Script.git
cd Wen-Script
```

### Run a Wen program

Create a file called `hello.wen`:

```wen
let message = "Hello from Wen!"
print(message)
```

Run it from the project directory:

```bash
python3 src/main.py hello.wen
```

## 3. Variables and Expressions

Wen uses `let` to declare variables.

```wen
let first = 10
let second = 5
let result = first + second

print(result)
```

Wen supports arithmetic operators including:

- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `%` Modulo

Comparison operators include:

- `==` Equal to
- `!=` Not equal to
- `<` Less than
- `>` Greater than
- `<=` Less than or equal to
- `>=` Greater than or equal to

## 4. Conditional Statements

Wen supports `if` and `else` statements.

```wen
let age = 20

if age >= 18 {
    print("Adult")
} else {
    print("Under 18")
}
```

Conditions allow a program to choose between different execution paths.

## 5. Loops

Wen supports `while` loops.

```wen
let count = 1

while count <= 5 {
    print(count)
    count = count + 1
}
```

The loop continues while its condition is true.

## 6. Functions

Wen supports user-defined functions with parameters and return values.

```wen
fn add(a, b) {
    return a + b
}

let result = add(10, 5)
print(result)
```

Functions can also call other functions:

```wen
fn multiply(a, b) {
    return a * b
}

fn calculate() {
    return multiply(4, 5)
}

print(calculate())
```

Current function capabilities include:

- User-defined functions
- Integer parameters
- Integer and decimal return values
- Nested function calls
- Zero-argument function calls

### Current limitations

Wen's function implementation is still developing:

- Function parameters currently support integer values.
- A return statement must be the final top-level statement in a function.
- Return statements inside conditional statements and loops are not yet supported.

## 7. How the Compiler Works

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

### Lexer

The lexer reads source code and converts it into tokens.

### Parser

The parser processes tokens and builds a structured representation of the program.

### Semantic Analysis

The semantic analyzer checks program meaning and validates supported language operations.

### LLVM Code Generation

The compiler translates the program into LLVM intermediate representation (LLVM IR).

### Native Compilation

Clang compiles the generated LLVM representation into a native executable.

## 8. Running the Tests

Wen includes automated tests for language and compiler functionality.

Run them using:

```bash
python3 -m unittest discover -s tests -v
```

## 9. Explore the Project

- [GitHub Repository](https://github.com/lampard1189-hub/Wen-Script)
- [Official Documentation](https://lampard1189-hub.github.io/Wen-Script/docs/)
- [Project Website](https://lampard1189-hub.github.io/Wen-Script/)
- [PyPI Package](https://pypi.org/project/wen-lang/)

## 10. What's Next?

Wen is actively experimental. Future development may include:

- Decimal function parameters
- Return statements inside conditional statements and loops
- Improved compiler diagnostics
- User-defined types
- Additional target architectures
- An expanded standard library
- More advanced memory management

Interested in helping? See [CONTRIBUTING.md](CONTRIBUTING.md).

---

Wen is an independent experimental programming-language project. Contributions, feedback, and suggestions are welcome.
