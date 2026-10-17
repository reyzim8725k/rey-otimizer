"""Operações de desinstalação conservadoras."""
import os, subprocess, shlex
PROTECTED = {"microsoft edge", "microsoft visual c++", "windows", "microsoft .net"}

def is_protected(name):
    n=name.lower()
    return any(x in n for x in PROTECTED)

def uninstall(app):
    if is_protected(app.name): raise PermissionError(f"Aplicativo protegido: {app.name}")
    if app.source == "store":
        cmd=["powershell", "-NoProfile", "-Command", f"Get-AppxPackage -Name '{app.name}' | Remove-AppxPackage"]
    elif app.uninstall:
        cmd = app.uninstall if isinstance(app.uninstall, list) else shlex.split(app.uninstall, posix=False)
    else: raise ValueError("Não há comando de desinstalação registrado.")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=600)
