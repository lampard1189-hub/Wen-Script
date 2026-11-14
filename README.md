# Wen Programming Language

**Wen** is an experimental, Python-inspired programming language that compiles source code into native executables using LLVM.

Wen is designed to explore programming-language design, compiler construction, semantic analysis, and native code generation.

**Current release:** `0.2.0a1`
**Development status:** Experimental alpha

## Key Features

- Python-inspired syntax
- Variable declarations using `let`
- Integer, decimal, string, and boolean values
- Arithmetic operations
- Comparison operators
- Output using `print()`
- Conditional statements using `if` and `else`
- Loops using `while`
- Variable assignment
- Semantic analysis
- LLVM intermediate representation (IR) generation
- Native executable compilation

## How Wen Works

Wen uses a compiler pipeline that transforms source code into a native executable.

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

Clang must be available on your system for native compilation.

## Installation

Install Wen from PyPI:

```bash
python3 -m pip install wen-lang==0.2.0a1
```

Verify the installation:

```bash
wen --help
```

## Your First Wen Program

Create a file named `hello.wen`:

```wen
let name = "Wen"
let version = 2

print("Hello from Wen!")
print(name)
print(version)
```

Compile and run it:

```bash
wen hello.wen
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

## Development Installation

To work with the source code:

```bash
git clone https://github.com/lampard1189-hub/Wen-Script.git
cd Wen-Script
```

Run Wen directly from the source:

```bash
python3 src/main.py examples/hello.wen
```

Run the automated tests:

```bash
python3 -m unittest discover -s tests -v
```

## Project Links

- **Official Website:** https://lampard1189-hub.github.io/Wen-Script/
- **GitHub Repository:** https://github.com/lampard1189-hub/Wen-Script
- **PyPI Package:** https://pypi.org/project/wen-lang/
- **Sitemap:** https://lampard1189-hub.github.io/Wen-Script/sitemap.xml

## Development Roadmap

Wen is actively experimental. Potential future improvements include:

- Expanded function support
- User-defined types
- Improved compiler diagnostics
- Additional target architectures
- Expanded standard library
- More advanced memory management

## Contributing

Contributions, suggestions, bug reports, and discussions are welcome.

Explore the repository and follow the project's development.

## License

See the `LICENSE` file for licensing information.

