# Wen Programming Language

**Wen** is an experimental, Python-inspired programming language that compiles source code into native executables using LLVM.

The initial release, **v0.1**, targets Apple Silicon (ARM64) on macOS.

## Features

- Variable declarations using `let`
- Integer and string values
- Boolean values
- Arithmetic operations: `+`, `-`, `*`, `/`, `%`
- Comparisons: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Output using `print()`
- Conditional statements: `if` and `else`
- Loops using `while`
- Variable assignment
- Semantic analysis
- LLVM intermediate representation generation
- Native executable compilation

## Requirements

- macOS on Apple Silicon (ARM64)
- Python 3
- LLVM and Clang
- Homebrew (recommended for installing LLVM)

## Installation

Install LLVM using Homebrew:

```bash
brew install llvm
```

Clone the repository:

```bash
git clone https://github.com/lampard1189-hub/Wen-Script.git
```

Enter the project directory:

```bash
cd Wen-Script
```

## Running Wen

Create a source file with the `.wen` extension.

Example:

```wen
let name = "Wen"
let version = 1

print(name)
print(version)
print("Welcome to Wen!")
```

Compile the program:

```bash
python3 src/main.py examples/hello.wen
```

Run the generated executable:

```bash
./build/hello
```

## Control Flow Example

```wen
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
```

## Project Structure

```text
Wen/
├── examples/
│   ├── hello.wen
│   ├── arithmetic.wen
│   └── control.wen
├── src/
│   ├── lexer/
│   │   └── lexer.py
│   ├── parser/
│   │   └── parser.py
│   ├── compiler/
│   │   ├── codegen.py
│   │   └── semantic.py
│   ├── runtime/
│   │   └── runtime.py
│   └── main.py
├── tests/
│   └── test_wen.py
├── build/
└── README.md
```

## Testing

Run the automated test suite:

```bash
python3 -m unittest discover -s tests -v
```

## Compilation Pipeline

Wen currently follows this compilation process:

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
  LLVM Codegen
       |
       v
    LLVM IR
       |
       v
  Native Executable
```

## Current Development Status

**Version:** 0.1.0

**Status:** Experimental initial release.

The current implementation is focused on integer operations, strings, variables, comparisons and basic control flow.

Future development may include:

- Functions
- User-defined types
- Better error messages
- Floating-point arithmetic
- Additional target architectures
- More advanced memory management
- Expanded standard library

## License

See the `LICENSE` file for licensing information.

