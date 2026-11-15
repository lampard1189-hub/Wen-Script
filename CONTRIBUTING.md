# Contributing to Wen

Thank you for your interest in contributing to Wen!

Wen is an experimental, Python-inspired programming language built around compiler development and LLVM-based native code generation.

Contributions, bug reports, documentation improvements, and ideas are welcome.

## 1. Before You Contribute

Before making a contribution:

1. Read the [README](README.md).
2. Review [LEARN.md](LEARN.md) to understand the language and compiler pipeline.
3. Check existing GitHub Issues to avoid duplicating work.
4. For significant changes, open an issue first to discuss the proposed approach.

## 2. Development Requirements

You will need:

- Python 3.10 or later
- Clang
- Git
- A supported development environment

## 3. Set Up the Development Environment

Clone the development branch:

```bash
git clone -b development/v0.2 https://github.com/lampard1189-hub/Wen-Script.git
cd Wen-Script
```

Check your Python version:

```bash
python3 --version
```

Check that Clang is available:

```bash
clang --version
```

If Clang is not available, install and configure an appropriate LLVM/Clang toolchain for your operating system.

## 4. Run Wen

Create or use a `.wen` source file.

For example:

```wen
let number = 10
print(number)
```

Run the program from the project directory:

```bash
python3 src/main.py examples/hello.wen
```

## 5. Run the Test Suite

Before submitting changes, run:

```bash
python3 -m unittest discover -s tests -v
```

Check that existing tests pass.

If you introduce new functionality, include tests that cover the new behavior and relevant edge cases.

## 6. Areas Where Contributions Are Welcome

The following areas are useful opportunities for contributors:

### Language Features

- Decimal function parameters
- Return statements inside conditional statements and loops
- Additional expressions and operators
- User-defined types

### Compiler Development

- Improved semantic analysis
- Better compiler diagnostics
- LLVM code generation improvements
- Additional target architectures

### Documentation

- Tutorials and examples
- Language reference documentation
- Compiler architecture explanations
- Installation instructions

### Testing

- Lexer tests
- Parser tests
- Semantic analysis tests
- Code generation tests
- Native compilation tests

These are development opportunities, not claims that the features are already implemented.

## 7. Contribution Workflow

A typical contribution follows these steps:

1. Find an existing issue or propose a new one.
2. Discuss substantial changes before implementation.
3. Create a separate branch for your work.
4. Make focused changes.
5. Add or update tests.
6. Run the test suite.
7. Review your changes.
8. Submit a pull request with a clear explanation.

Example branch creation:

```bash
git switch -c feature/your-feature-name
```

Use a descriptive branch name that explains the change.

## 8. Code Quality Guidelines

Please aim to:

- Keep changes focused and understandable.
- Follow the existing project structure.
- Use clear and descriptive names.
- Avoid unrelated modifications.
- Add tests for new functionality.
- Update documentation when language behavior changes.
- Clearly document known limitations.

## 9. Reporting Bugs

When reporting a bug, include:

- A short description of the problem
- Steps to reproduce it
- A minimal `.wen` example, if possible
- The expected behavior
- The actual behavior
- Your operating system and Python version
- Relevant error output

Never include passwords, access tokens, or other private credentials in an issue.

## 10. Feature Proposals

For feature requests, explain:

- What the proposed feature should do
- Why it would be useful
- An example of the intended Wen syntax
- Any compatibility or implementation considerations

Large language changes should be discussed before implementation.

## 11. Pull Requests

A good pull request should:

- Explain what changed and why.
- Reference related issues where applicable.
- Include tests for new behavior.
- Update relevant documentation.
- Avoid unrelated file changes.

Please be patient while contributions are reviewed. Wen is experimental, and proposed changes may require discussion or revision.

## 12. Project Status

Wen is an experimental project under active development. APIs, syntax, compiler behavior, and project structure may change.

Contributing does not guarantee that a proposed feature will be accepted, but thoughtful feedback and technical discussion are appreciated.

Thank you for helping improve Wen!
