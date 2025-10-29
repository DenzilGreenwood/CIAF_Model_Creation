# CIAF VS Code Setup - AI Agent Automation

This directory contains a comprehensive VS Code development environment setup for the Cognitive Insight Audit Framework (CIAF) with automated AI agent workflows.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
python setup_vscode.py
```

### Option 2: Manual PowerShell Setup
```powershell
.\ai-agent-setup.ps1 workflow
```

### Option 3: VS Code Workspace
```bash
code CIAF_Workspace.code-workspace
```

## 📁 Setup Components

### VS Code Configuration (`.vscode/`)
- **`settings.json`** - Python environment, linting, formatting, and CIAF-specific settings
- **`tasks.json`** - Automated tasks for testing, demos, validation, and quality checks
- **`launch.json`** - Debug configurations for all CIAF scripts and demos
- **`extensions.json`** - Recommended extensions for optimal development experience

### Project Configuration
- **`pyproject.toml`** - Modern Python project configuration with CIAF package metadata
- **`requirements.txt`** - Core dependencies for CIAF framework
- **`requirements-dev.txt`** - Development tools and testing dependencies
- **`.pre-commit-config.yaml`** - Git hooks for code quality and compliance validation

### AI Agent Automation
- **`ai-agent-setup.ps1`** - PowerShell script for automated workflows
- **`.ciaf-agent-config.yaml`** - Configuration for AI agent behaviors and capabilities
- **`setup_vscode.py`** - Python setup script for complete environment configuration

## 🎯 AI Agent Workflows

### Development Workflow
```powershell
.\ai-agent-setup.ps1 workflow
```
1. ✅ Prerequisites check
2. 📦 Install dependencies  
3. 🔍 Framework validation
4. 🧪 Code quality checks
5. 🧪 Run tests
6. 🎭 Run demos

### Individual Commands
```powershell
# Install dependencies
.\ai-agent-setup.ps1 install

# Run specific tests
.\ai-agent-setup.ps1 test unit
.\ai-agent-setup.ps1 test compliance

# Run specific demos
.\ai-agent-setup.ps1 demo healthcare
.\ai-agent-setup.ps1 demo banking
.\ai-agent-setup.ps1 demo government

# Code quality checks
.\ai-agent-setup.ps1 quality

# Framework validation
.\ai-agent-setup.ps1 validate

# Generate investor package
.\ai-agent-setup.ps1 investor

# Clean workspace
.\ai-agent-setup.ps1 clean

# Start documentation server
.\ai-agent-setup.ps1 docs
```

## 🔧 VS Code Tasks

Access via `Ctrl+Shift+P` → "Tasks: Run Task":

### Build Tasks
- **CIAF: Install Dependencies** - Install all Python packages
- **CIAF: AI Agent Workflow** - Complete automated workflow
- **CIAF: Format Code** - Auto-format with Black + isort
- **CIAF: Clean Build Artifacts** - Remove cache and temp files

### Test Tasks
- **CIAF: Run All Tests** - Execute full test suite with coverage
- **CIAF: Code Quality Check** - MyPy, Bandit, pytest with coverage
- **CIAF: Validate Frameworks** - Compliance framework validation
- **CIAF: Validate Regulatory Mappings** - Regulatory compliance check

### Demo Tasks
- **CIAF: Healthcare Demo** - FDA SaMD compliance demonstration
- **CIAF: Banking Demo** - Federal Reserve SR 11-7 compliance
- **CIAF: Government Demo** - OMB M-24-10 transparency compliance
- **CIAF: Citation Anchor Demo** - IP and data usage tracking
- **CIAF: Run All Demos** - Execute all demonstration scenarios

### Utility Tasks
- **CIAF: Verify Receipts** - Cryptographic receipt validation
- **CIAF: ROI Benchmarks** - Performance and ROI analysis
- **CIAF: Generate Investor Package** - Due diligence materials
- **CIAF: Start Documentation Server** - Local docs at localhost:8000

## 🐛 Debug Configurations

Press `F5` or use Debug panel:

### Available Configurations
- **CIAF: Debug Current File** - Debug the currently open Python file
- **CIAF: Debug Citation Anchor Demo** - Debug citation tracking system
- **CIAF: Debug Healthcare Demo** - Debug FDA compliance demo
- **CIAF: Debug Banking Demo** - Debug SR 11-7 compliance demo
- **CIAF: Debug Government Demo** - Debug OMB M-24-10 demo
- **CIAF: Debug Framework Validation** - Debug compliance validation
- **CIAF: Debug Tests** - Debug test execution
- **CIAF: Debug Specific Test** - Debug currently open test file

### Debug Features
- ✅ Automatic PYTHONPATH configuration
- ✅ Integrated terminal debugging
- ✅ Return value inspection
- ✅ Step-through debugging for all CIAF components
- ✅ Remote debugging support (port 5678)

## 📚 Recommended Extensions

Auto-installed via `extensions.json`:

### Core Python Development
- **Python** (ms-python.python) - Core Python support
- **Python Debugger** (ms-python.debugpy) - Enhanced debugging
- **Black Formatter** (ms-python.black-formatter) - Code formatting
- **Flake8** (ms-python.flake8) - Linting
- **isort** (ms-python.isort) - Import sorting
- **MyPy** (ms-python.mypy-type-checker) - Type checking

### Data Science & ML
- **Jupyter** (ms-toolsai.jupyter) - Notebook support
- **TensorBoard** (ms-toolsai.tensorboard) - ML visualization
- **Data Wrangler** (ms-toolsai.datawrangler) - Data exploration

### Documentation & LaTeX
- **LaTeX Workshop** (james-yu.latex-workshop) - LaTeX compilation
- **Markdown All in One** (yzhang.markdown-all-in-one) - Markdown tools

### Git & Collaboration
- **GitLens** (eamodio.gitlens) - Enhanced Git integration
- **GitHub Pull Requests** (github.vscode-pull-request-github) - PR management
- **GitHub Copilot** (github.copilot) - AI code assistance
- **GitHub Copilot Chat** (github.copilot-chat) - AI conversation

### Code Quality & Security
- **SonarLint** (sonarsource.sonarlint-vscode) - Code quality
- **Security Scan** (ms-vscode.vscode-security-scan) - Security analysis

## ⚙️ Configuration Details

### Python Environment
- **Interpreter**: `D:/python312/python.exe` (configurable)
- **Auto-activation**: Terminal environment activation
- **Path**: Automatic PYTHONPATH setup for CIAF modules

### Code Quality
- **Formatting**: Black (100 char line length)
- **Linting**: Flake8 + MyPy with strict typing
- **Security**: Bandit security scanning
- **Import sorting**: isort with Black profile

### Testing
- **Framework**: pytest with coverage reporting
- **Markers**: unit, integration, compliance, security, performance
- **Coverage**: HTML reports in `htmlcov/`
- **Auto-discovery**: Automatic test detection and execution

### Pre-commit Hooks
- ✅ Code formatting (Black + isort)
- ✅ Linting (Flake8 + MyPy)
- ✅ Security scanning (Bandit)
- ✅ CIAF compliance validation
- ✅ Citation anchor validation
- ✅ Cryptographic health checks

## 🚨 Troubleshooting

### Common Issues

#### Citation Anchor Error
```
TypeError: AuditTrailGenerator.__init__() missing 1 required positional argument: 'model_name'
```
**Solution**: The setup script fixes this automatically, or run:
```powershell
.\ai-agent-setup.ps1 workflow
```

#### Import Errors
```
ModuleNotFoundError: No module named 'ciaf'
```
**Solution**: Install in development mode:
```bash
pip install -e .
```

#### VS Code Extension Issues
**Solution**: Reinstall extensions:
```bash
python setup_vscode.py --skip-validation
```

#### Permission Errors on Windows
**Solution**: Run PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Validation Commands
```bash
# Check Python environment
python -c "import ciaf; print(f'CIAF version: {ciaf.__version__}')"

# Validate frameworks
python scripts/validate_frameworks.py

# Test basic functionality
python -m pytest tests/ -v --tb=short

# Check code quality
python -m mypy ciaf/ --ignore-missing-imports
```

## 📞 Support

### Getting Help
- **Documentation**: Start local server with `.\ai-agent-setup.ps1 docs`
- **Examples**: Run demos with `.\ai-agent-setup.ps1 demo all`
- **Issues**: Check the troubleshooting section above
- **Validation**: Use `.\ai-agent-setup.ps1 validate` for health checks

### Key Files
- **Main Module**: `ciaf/__init__.py`
- **Demo Scripts**: `examples/golden_paths/`
- **Tests**: `tests/`
- **Documentation**: `Docs/`
- **Configuration**: `pyproject.toml`

---

**🎉 You're all set!** The CIAF VS Code environment is configured for optimal AI agent automation and development productivity.

Happy coding with evidence-first AI governance! 🤖✨