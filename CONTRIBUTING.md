# Contributing to NL2SQL Tool

Thank you for your interest in contributing to the NL2SQL Tool! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:

1. Clear, descriptive title
2. Steps to reproduce the bug
3. Expected behavior
4. Actual behavior
5. Screenshots if applicable
6. Your environment details (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please create an issue with:

1. Clear description of the feature
2. Rationale for why it would be valuable
3. Possible implementation ideas (optional)

### Pull Requests

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Write/update tests as needed
5. Ensure all tests pass
6. Submit a pull request

## Development Setup

1. Clone the repository
2. Set up a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies
   ```bash
   pip install -r requirements-dev.txt
   ```
4. Run tests
   ```bash
   pytest
   ```

## Style Guidelines

- We use Black for code formatting
- Follow PEP 8 guidelines
- Use type hints where possible
- Write meaningful docstrings
- Keep functions small and focused

## Testing

- All new features should include tests
- All bug fixes should include tests that reproduce the bug
- Run the full test suite before submitting a PR

## Documentation

- Update documentation for any code changes
- Make sure examples in the docs work
- Keep the README.md up to date

## Commit Messages

Write clear, descriptive commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
