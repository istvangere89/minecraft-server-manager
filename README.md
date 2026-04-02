# Minecraft Server Manager Setup Guide

## Overview
Minecraft Server Manager is a Python-based desktop application (Windows) that helps you manage multiple Bedrock server configurations with password protection.

## Features
- **List Configurations**: Automatically discovers all `server-*.properties` files with their World names
- **Password Protection**: Optionally protect configurations with passwords (hashed SHA256)
- **One-Click Start**: Select a config → copy to `server.properties` → start the server
- **Configuration Management**: Change server directory, manage passwords

## Initial Setup

### 1. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Pre-Commit Hooks (Optional but Recommended)
Pre-commit hooks run code quality checks before each commit:

```bash
# Install pre-commit
pip install pre-commit

# Set up the git hooks
pre-commit install

# Run checks on all files manually (optional)
pre-commit run --all-files
```

The hooks will run automatically on `git commit` and check:
- Code formatting (black)
- Import organization (isort)
- Syntax errors

## Code Quality Configuration

All code quality tools use **centralized configuration** for consistency between local development and CI/CD:

### Configuration Files

**`pyproject.toml`** - Main configuration file:
- `[tool.black]` - Code formatter (120 char line length)
- `[tool.isort]` - Import organizer (black-compatible profile)
- `[tool.mypy]` - Type checker (optional, run manually)
- `[tool.pylint]` - Linter (optional, run manually)
- `[tool.coverage]` - Test coverage settings

**`.flake8`** - Flake8 linter configuration:
- `max-line-length = 120`
- `ignore = E501, W503`

### Running Quality Checks

**Automatic (on commit via pre-commit):**
```bash
git commit -m "my changes"  # Runs black, isort, flake8 automatically
```

**Manual (run all checks):**
```bash
pre-commit run --all-files
```

**Individual tools:**
```bash
black *.py ui/*.py          # Auto-format code
isort *.py ui/*.py          # Organize imports
flake8 *.py ui/*.py         # Check linting
```

### CI/CD Workflow

GitHub Actions workflow (`.github/workflows/build.yml`) runs the same quality checks:
- ✅ **Blocking checks** (fail the build): black, isort, syntax, tests
- ⚠️ **Advisory checks** (warnings only): flake8

All tools automatically read from centralized configs above.

### 4. Configure Server Directory
On first run, the application will prompt you to select your Minecraft Bedrock server directory. Ensure:
- The directory contains `bedrock_server.exe`
- You have `server-*.properties` files in the directory (e.g., `server-world1.properties`)

### 5. Set Up Your Server Configurations
Create config files in your server directory:
```
C:\path\to\server\server-world1.properties
C:\path\to\server\server-world2.properties
```

Each file should contain:
```
level-name=My World
# ... other server properties
```

## Running the Application

### Development Mode
```bash
python main.py
```

### Build Standalone Executable
The app can be packaged as a standalone `.exe` for easy distribution:

```bash
# First, install PyInstaller
pip install pyinstaller

# Run build script (Windows)
build.bat

# Or (Linux/Mac)
bash build.sh
```

The executable will be created at: `dist\minecraft_server_manager.exe`

You can then:
1. Place it on your Desktop
2. Add a custom Minecraft icon
3. Run without needing Python installed

## Icon Setup
Replace `assets/app_icon.ico` with a custom Minecraft-themed icon:
- Format: `.ico` file (256x256px recommended)
- The icon will be embedded in the standalone executable

## Configuration Storage
App settings are saved in `minecraft_server_manager_config.json`:
- Server directory path
- Protected config names and password hashes

Keep this file in the same directory as the executable.

## File Structure
```
minecraft-server-manager/
├── main.py                    # Entry point
├── config.py                  # Configuration management
├── password_manager.py        # Password hashing/verification
├── server_manager.py          # File operations and server control
├── ui/
│   ├── __init__.py
│   ├── main_window.py        # Main UI window
│   └── dialogs.py            # Password/directory dialogs
├── assets/
│   └── app_icon.ico          # Application icon
├── requirements.txt          # Python dependencies
├── build.spec                # PyInstaller spec file
├── build.bat                 # Windows build script
├── build.sh                  # Linux/Mac build script
└── README.md                 # This file
```

## Troubleshooting

### "bedrock_server.exe not found"
- Make sure you've selected the correct server directory
- Check that `bedrock_server.exe` exists in that directory

### "No configurations found"
- Ensure you have `server-*.properties` files in your server directory
- The app looks for files matching pattern: `server-*.properties`
- Each file must contain a `level-name=` property

### Password not working
- Passwords are case-sensitive
- Check Caps Lock
- If you forget a password, delete `minecraft_server_manager_config.json` to reset

## Future Enhancements
- Update checker for new Bedrock server versions
- Server console integration
- Backup/restore configurations
- Multiple server profile support

## License
Free to use and modify for personal use.
