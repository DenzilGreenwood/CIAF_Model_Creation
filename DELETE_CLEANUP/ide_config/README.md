# IDE Configuration Files Moved to DELETE_CLEANUP

This directory contains IDE-specific configuration files that were removed from the main repository.

## Files Moved Here:

### `.vscode/` directory
- **Contents:** VS Code workspace settings, launch configurations, tasks
- **Reason for removal:** IDE configurations should be user-specific
- **Impact:** Developers need to configure their own VS Code settings

### `CIAF_Workspace.code-workspace`
- **Purpose:** VS Code workspace file
- **Reason for removal:** Workspace configurations are environment-specific
- **Impact:** Developers can create their own workspace files

### `VSCODE_SETUP_README.md`
- **Purpose:** VS Code setup documentation
- **Reason for removal:** IDE-specific documentation not needed for core project
- **Impact:** VS Code users need to configure manually

### `setup_vscode.py`
- **Purpose:** Automated VS Code configuration script
- **Reason for removal:** Environment-specific setup scripts
- **Impact:** Manual VS Code configuration required

## Recommendations:

### For VS Code Users:
1. Create your own `.vscode/settings.json` with preferred settings
2. Configure Python interpreter path for your environment
3. Set up preferred extensions and themes
4. Create personal workspace file if needed

### For Other IDEs:
- Configure your preferred IDE according to its documentation
- Set up Python path and interpreter
- Configure linting and formatting tools as preferred

## Why Remove IDE Configs?

1. **User Preference:** Different developers prefer different IDE settings
2. **Environment Specific:** Paths and configurations vary by machine
3. **Version Control Pollution:** IDE files change frequently and pollute git history
4. **Conflicts:** Different IDE versions may have incompatible configurations

## Alternative Approach:

Consider creating a `docs/development-setup.md` file with:
- Recommended IDE extensions
- Suggested configuration settings
- Setup instructions for common IDEs
- Development workflow guidelines

This approach provides guidance without forcing specific configurations.