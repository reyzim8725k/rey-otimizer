# 🛡️ Rey Optimizer

A purple-themed Python desktop panel for Windows diagnostics, monitoring and cautious maintenance.

This is a functional development prototype. Test in a virtual machine first. It asks for confirmation before destructive actions, uses official uninstall commands, protects critical application names, and writes daily logs.

## Install

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Build

```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --uac-admin --name "Rey Optimizer" main.py
```

See [README.md](README.md) for the complete Portuguese documentation.
