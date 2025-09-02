---
trigger: manual
---

**Default Working Directory Rule:**
- All work must be performed in the `dividend-in-korea` directory by default
- Always change to `dividend-in-korea` directory before executing any commands or analysis
- This directory contains the Korean dividend analysis system with proper Korean font support

**Python Execution Rules:**
- Run Python code using the command `uv run python` 
- Use the command `uv add` when you need to add additional modules
- All Python scripts should be executed from within the `dividend-in-korea` directory

**Testing Requirements:**
- Make unit tests & show the results with table
- Use `.
un.ps1 unittest` for comprehensive unit testing
- Ensure Korean text (한글) display is properly tested
- Use `.
write the results of unittest in README_KOREAN.md as table in detail