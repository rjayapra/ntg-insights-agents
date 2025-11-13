# Contributing to NTG Insights Agents

Thank you for your interest in contributing to this project! This document provides guidelines for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/ntg-insights-agents.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest tests/`
6. Commit your changes: `git commit -m "Add feature: description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

### Install Development Dependencies

```bash
pip install -e .
pip install -r requirements-dev.txt
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=ntg_insights_agents tests/

# Run specific test file
pytest tests/test_config_parser.py -v
```

## Coding Standards

### Python Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

### Documentation

- Update README.md if you add new features
- Add docstrings to new functions/classes
- Update QUICKSTART.md for user-facing changes
- Add examples for new functionality

### Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting PR
- Aim for good test coverage (>80%)
- Use meaningful test names that describe what is being tested

## Pull Request Guidelines

### Before Submitting

1. **Run Tests**: Ensure all tests pass
   ```bash
   pytest tests/ -v
   ```

2. **Check Coverage**: Verify test coverage
   ```bash
   pytest --cov=ntg_insights_agents tests/
   ```

3. **Update Documentation**: Add/update relevant documentation

4. **Test Examples**: Verify example configurations work
   ```bash
   ntg-agent validate examples/*.yaml
   ```

### PR Description

Include in your PR description:

- **What**: Brief description of changes
- **Why**: Reason for the changes
- **How**: How the changes work
- **Testing**: What testing you performed
- **Screenshots**: If applicable (for CLI changes)

### Example PR Description

```
## What
Added support for custom tool configurations in agent YAML files

## Why
Users need to be able to define custom tools for their agents

## How
- Extended config_parser.py to parse tool definitions
- Updated agent_creator.py to pass tools to Azure SDK
- Added validation for tool configurations

## Testing
- Added unit tests for tool parsing
- Tested with sample tool configuration
- Verified existing tests still pass
```

## Code Review Process

1. **Submit PR**: Create pull request with clear description
2. **Review**: Maintainers will review your code
3. **Feedback**: Address any feedback or requested changes
4. **Approval**: Once approved, PR will be merged

## Types of Contributions

### Bug Fixes

- Report bugs via GitHub Issues
- Include reproduction steps
- Submit PR with fix and tests

### New Features

- Discuss in GitHub Issues first
- Get consensus on approach
- Implement with tests and documentation
- Submit PR

### Documentation

- Fix typos or unclear sections
- Add examples or tutorials
- Improve code comments
- Update README or guides

### Examples

- Add new example agent configurations
- Improve existing examples
- Add use case documentation

## Commit Message Guidelines

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add validation for tool configurations"
git commit -m "Fix bug in YAML parser for nested options"
git commit -m "Update README with new CLI commands"

# Not as good
git commit -m "Fix bug"
git commit -m "Update"
git commit -m "Changes"
```

## Questions?

- Open an issue for questions
- Check existing issues and PRs first
- Contact the maintainers via GitHub

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help create a welcoming environment
- Follow GitHub's community guidelines

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing!
