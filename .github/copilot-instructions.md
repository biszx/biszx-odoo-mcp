---
applyTo: '**'
---

# Tech Stack

This repository uses the following technologies:

- **Python**: The primary programming language for the project.
- **MCP**: The MCP (Model Context Protocol) is used for managing and controlling the model lifecycle.

# Project Structure

The project follows a modular structure, with separate directories for different components:

- **src/**: Contains the main source code for the project.
- **tests/**: Contains unit tests and test data.

# Project Configuration

- **pyproject.toml**: The main configuration file for the project, specifying dependencies and build settings.
- **.flake8**: Configuration file for Flake 8, a tool for checking the style guide enforcement.
- **.pylintrc**: Configuration file for Pylint, a static code analysis tool.
- **.ruff.toml**: Configuration file for Ruff, a fast Python linter and formatter.
- **pytest.ini**: Configuration file for pytest, the testing framework used in the project.

# Project Setup

- Using `uv` to use as setup environment.

# Following Rules

## Coding

- **Code Style**: Follow Flake 8, Pylint, and Ruff guidelines for Python code.
- **Documentation**: Always document your code using docstrings, comments and README files.
- **Testing**: Write unit tests for your code using `pytest` with 100% line coverage.

## AI Steps

1. **Understanding the Code**: Analyze the existing codebase to understand its structure and functionality.
2. **Identifying Areas for Improvement**: Look for code smells, inefficiencies, or areas lacking test coverage.
3. **Implementing Changes**: Make the necessary code changes to improve the codebase, following best practices.
4. **Testing**: Ensure all changes are covered by tests and that the tests pass successfully.
5. **Documentation**: Update `README.md` in `Features`, `Tools` and `Resources` sections to reflect any changes made, including new features or tools added.
6. **Code Review**: Submit changes for review, ensuring they meet the project's coding standards and guidelines.
