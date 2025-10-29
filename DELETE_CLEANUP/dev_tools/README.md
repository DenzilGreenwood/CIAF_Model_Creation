# Development Tools Moved to DELETE_CLEANUP

This directory contains development tools and configurations that were removed from the main repository.

## Files Moved Here:

### `.pre-commit-config.yaml`
- **Purpose:** Pre-commit hooks configuration
- **Reason for removal:** Development workflow tool, not essential for core functionality
- **Impact:** Developers need to set up own pre-commit hooks if desired

### `requirements-dev.txt`
- **Purpose:** Development dependencies (testing, linting, etc.)
- **Reason for removal:** Separating development dependencies from runtime requirements
- **Impact:** Developers need to identify and install development tools manually

### `ai-agent-setup.ps1`
- **Purpose:** PowerShell script for AI agent configuration
- **Reason for removal:** Environment-specific setup script
- **Impact:** Manual setup required for AI development tools

### `.ciaf-agent-config.yaml`
- **Purpose:** AI agent configuration file
- **Reason for removal:** Development tool configuration
- **Impact:** AI development workflows need manual configuration

## Development Tool Alternatives:

### Pre-commit Hooks
If you want to use pre-commit hooks, create your own `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
```

### Development Dependencies
Essential development tools to consider installing:
```bash
pip install pytest pytest-cov mypy black flake8 bandit
```

### AI Development Tools
If using AI-assisted development:
- Configure your preferred AI coding assistant
- Set up API keys and configurations according to tool documentation
- Create personal configuration files

## Why Remove Development Tools?

1. **Flexibility:** Allows developers to choose their preferred tools
2. **Environment Independence:** Avoids conflicts with existing developer setups
3. **Simplicity:** Keeps the core repository focused on essential functionality
4. **Personal Preference:** Development workflows are highly personal

## Recommended Approach:

Create a `docs/development-guide.md` with:
- Recommended development tools
- Setup instructions for common scenarios
- Testing guidelines
- Code quality standards
- Development workflow suggestions

This provides guidance without enforcing specific tool choices.