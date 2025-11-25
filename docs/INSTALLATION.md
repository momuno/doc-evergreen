# Installing doc-evergreen

Complete installation guide for doc-evergreen v0.4.1+

---

## Quick Install

### Using pipx (Recommended)

**pipx is STRONGLY recommended** - it handles virtual environments automatically and works on all systems including those with externally-managed Python (Debian/Ubuntu).

```bash
# Install pipx if you don't have it
pip install --user pipx  # or: apt install pipx

# Install doc-evergreen
pipx install git+https://github.com/momuno/doc-evergreen.git

# Or from local clone:
git clone https://github.com/momuno/doc-evergreen.git
pipx install -e ./doc-evergreen
```

### Using pip (Not Recommended on Modern Linux)

⚠️ **Modern Linux systems block pip install to system Python.** Use pipx instead.

If you're in a virtual environment or sure you want to proceed:

```bash
pip install git+https://github.com/momuno/doc-evergreen.git
```

### Development Installation

For contributing:

```bash
git clone https://github.com/momuno/doc-evergreen.git
cd doc-evergreen

# Use pipx (recommended)
pipx install -e .

# Or create dedicated venv
python3 -m venv ~/.venvs/doc-evergreen
~/.venvs/doc-evergreen/bin/pip install -e .
```

---

## Verification

Verify installation succeeded:

```bash
doc-evergreen --help
```

You should see:
```
Usage: doc-evergreen [OPTIONS] COMMAND [ARGS]...

  doc-evergreen - AI-powered documentation generation.
  ...
```

---

## Set Up API Key (Required)

doc-evergreen uses Anthropic's Claude for AI generation. You need an API key:

### Get API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Create an API key

### Configure API Key

**Option 1: Environment variable** (recommended for testing)
```bash
export ANTHROPIC_API_KEY=your_key_here
```

**Option 2: Add to shell profile** (permanent)
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export ANTHROPIC_API_KEY=your_key_here' >> ~/.bashrc
source ~/.bashrc
```

**Verify API key is set:**
```bash
echo $ANTHROPIC_API_KEY  # Should show your key
```

---

## First Project

Get started in <5 minutes:

```bash
# 1. Navigate to your project
cd /path/to/your-project

# 2. Initialize doc-evergreen
doc-evergreen init

# 3. (Optional) Customize the generated template
nano .doc-evergreen/readme.json

# 4. Generate documentation
doc-evergreen regen-doc readme
```

---

## Requirements

- **Python**: 3.11 or higher
- **Dependencies**: Installed automatically
  - click (CLI framework)
  - pydantic-ai (AI generation)

---

## Finding Your Installation

Not sure how or where doc-evergreen was installed? Run these commands:

```bash
# Find the executable location
which doc-evergreen

# Check if installed via pipx
pipx list | grep doc-evergreen

# Check if installed via pip
pip show doc-evergreen
```

**Expected outputs:**
- **pipx**: Shows "package doc-evergreen X.X.X, installed using Python..."
- **pip**: Shows "Location: /path/to/site-packages"
- **Not found**: Command not found or no output

---

## Uninstalling

### If installed with pipx (Recommended method):

```bash
# Uninstall
pipx uninstall doc-evergreen

# Verify it's gone
doc-evergreen --version  # Should show "command not found"
```

### If installed with pip:

```bash
# Uninstall
pip uninstall doc-evergreen

# Or if in a virtual environment
/path/to/venv/bin/pip uninstall doc-evergreen

# Verify it's gone
doc-evergreen --version  # Should show "command not found"
```

### If installed with pip -e (editable/development):

```bash
# From the doc-evergreen directory
pip uninstall doc-evergreen

# This removes the link but keeps the source code
# Delete the source directory if you're done with it
```

### Clean up shell configuration (if needed):

If you added doc-evergreen to your PATH manually, remove these lines from `~/.bashrc` or `~/.zshrc`:
```bash
# Remove lines like these if present:
export PATH="/path/to/doc-evergreen:$PATH"
alias doc-evergreen='...'
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

---

## Troubleshooting

### pip: externally-managed-environment ⚠️ COMMON ISSUE

**Symptom**:
```
error: externally-managed-environment
× This environment is externally managed
```

**Cause**: Modern Debian/Ubuntu systems (PEP 668) block pip install to system Python.

**Solution (IMMEDIATE)**: Use pipx instead of pip:

```bash
# Install pipx (one time)
sudo apt install pipx
# or: pip install --user pipx

# Install doc-evergreen with pipx
pipx install -e /path/to/doc-evergreen

# Verify
doc-evergreen --help
```

**Alternative**: Create dedicated virtual environment:

```bash
python3 -m venv ~/.venvs/doc-evergreen
~/.venvs/doc-evergreen/bin/pip install -e /path/to/doc-evergreen

# Add alias to ~/.bashrc:
alias doc-evergreen='~/.venvs/doc-evergreen/bin/doc-evergreen'
```

**DO NOT use** `--break-system-packages` - pipx is cleaner.

### Command not found after installation

**Symptom**: `doc-evergreen: command not found`

**Solutions**:

1. **pipx path issue**: Ensure pipx bin directory is in PATH
   ```bash
   pipx ensurepath
   # Restart shell
   ```

2. **pip user install**: Add user bin to PATH
   ```bash
   # Add to ~/.bashrc or ~/.zshrc:
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. **Verify installation**:
   ```bash
   pip list | grep doc-evergreen
   ```

### Import errors

**Symptom**: `ModuleNotFoundError: No module named 'doc_evergreen'`

**Solution**: Reinstall the package:
```bash
pip uninstall doc-evergreen
pip install git+https://github.com/momuno/doc-evergreen.git
```

### Permission denied

**Symptom**: Permission error during installation

**Solution**: Use --user flag or virtual environment:
```bash
pip install --user git+https://github.com/momuno/doc-evergreen.git
```

### Python version too old

**Symptom**: `requires python >=3.11`

**Solution**: Upgrade Python or use pyenv:
```bash
# Check current version
python --version

# Install Python 3.11+ with pyenv (recommended)
pyenv install 3.11
pyenv local 3.11
```

---

## Platform-Specific Notes

### Linux/macOS

Installation works out of the box. Use your system package manager to install Python 3.11+ if needed.

### Windows

1. Install Python 3.11+ from python.org
2. Ensure Python is in PATH
3. Use PowerShell or Command Prompt for installation

### WSL (Windows Subsystem for Linux)

Works same as native Linux. Recommended over native Windows for better path handling.

---

## Updating

To update to the latest version:

### pipx:
```bash
pipx upgrade doc-evergreen
```

### pip:
```bash
pip install --upgrade git+https://github.com/momuno/doc-evergreen.git
```

### Development installation:
```bash
cd /path/to/doc-evergreen
git pull
pip install -e .
```

---

## Next Steps

After installation:

1. **Read the User Guide**: See `docs/USER_GUIDE.md` for complete workflows
2. **Review Best Practices**: See `docs/BEST_PRACTICES.md` for template design patterns
3. **Check Examples**: See `examples/` directory for template examples
4. **Join the Community**: Report issues, request features, contribute

---

## Support

- **Issues**: https://github.com/momuno/doc-evergreen/issues
- **Discussions**: https://github.com/momuno/doc-evergreen/discussions
- **Documentation**: See repository README and docs/

---

**Installation takes <2 minutes. First doc generation in <5 minutes.**
