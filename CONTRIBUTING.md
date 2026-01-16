# Contributing to AlphaMapping

Thank you for your interest in contributing to AlphaMapping! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/AlphaMapping.git`
3. Create a branch: `git checkout -b feature/your-feature-name`

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check existing issues. When creating a bug report, include:

- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs **actual behavior**
- **Screenshots** if applicable
- **Environment details** (OS, Python version, browser)

### Suggesting Features

Feature requests are welcome! Please include:

- **Clear description** of the feature
- **Use case** - why is this feature needed?
- **Possible implementation** approach (optional)

### Code Contributions

1. Check open issues or create a new one to discuss changes
2. Fork and create a feature branch
3. Write code following our [Code Style](#code-style)
4. Add tests if applicable
5. Submit a Pull Request

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start development server
uvicorn app.main:app --reload
```

### Frontend

```bash
# Serve frontend with any static server
cd frontend
python -m http.server 3000
```

### Docker

```bash
docker-compose up -d
```

## Code Style

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters

```python
def example_function(param1: str, param2: int) -> dict:
    """
    Brief description of the function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    pass
```

### JavaScript (Frontend)

- Use ES6+ syntax
- Use `const` and `let` instead of `var`
- Add comments for complex logic
- Use meaningful variable names

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(api): add asset export endpoint
fix(ui): resolve chart rendering issue on Firefox
docs(readme): update installation instructions
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**: `pytest tests/ -v`
4. **Update CHANGELOG.md** with your changes
5. **Request review** from maintainers

### PR Title Format

Use the same format as commits:
```
feat(api): add scheduled task management
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing done

## Screenshots (if applicable)
```

## Questions?

Feel free to open an issue for any questions about contributing.

---

Thank you for contributing to AlphaMapping! 🎉
