# Assembler Compiler

A coursework project, implementing a simplified compiler for an assembly-like language in Python.

## 📌 Features

- **Lexical Analyzer**  
  Identifies and classifies tokens including instructions, identifiers, constants, and directives.

- **Two-Pass Assembler**  
  Implements a two-pass compilation system for symbol resolution and code generation.

- **Supported Directives**  
  - `SEGMENT`, `ENDS`
  - `DB`, `DD`
  - `EQU`, `ASSUME`, etc.

- **Instruction Encoding**  
  Handles instructions with register and memory operands.

- **Output**  
  - Symbol table  
  - Lexeme table  
  - Intermediate and final machine code

## 🛠️ Tech Stack

- Python 3.x  
- CLI-based interface  
- Custom parsing and file handling

## 📈 Example Output

- Intermediate code (first pass)  
- Resolved machine code (second pass)  
- Tables printed to console or saved to file
