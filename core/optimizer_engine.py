"""Ações de manutenção Windows; nenhuma é executada sem chamada explícita."""
import os, shutil, subprocess, tempfile

def temp_size():
    total=0
    for root, _, files in os.walk(tempfile.gettempdir()):
        for f in files:
            try: total += os.path.getsize(os.path.join(root,f))
            except OSError: pass
    return total

def clean_temp():
    removed=0
    for root, dirs, files in [(tempfile.gettempdir(), [], [])]:
        for name in os.listdir(root):
            p=os.path.join(root,name)
            try:
                if os.path.isdir(p): shutil.rmtree(p, ignore_errors=True)
                else: os.remove(p)
                removed += 1
            except OSError: pass
    return removed

def flush_dns():
    if os.name != "nt": raise OSError("Disponível somente no Windows")
    return subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, timeout=30)

def system_restore_point():
    if os.name != "nt": raise OSError("Disponível somente no Windows")
    return subprocess.run(["powershell", "-NoProfile", "-Command", "Checkpoint-Computer -Description 'Rey Optimizer backup' -RestorePointType MODIFY_SETTINGS"], capture_output=True, text=True, timeout=180)
