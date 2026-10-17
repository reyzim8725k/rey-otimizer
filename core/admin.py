"""Privilégios administrativos no Windows."""
import ctypes, os, sys

def is_admin() -> bool:
    if os.name != "nt": return False
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception: return False

def ensure_admin():
    if os.name != "nt": return
    if is_admin(): return
    params = " ".join(f'"{a}"' for a in sys.argv)
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    if rc <= 32: raise RuntimeError("Não foi possível solicitar elevação UAC.")
    raise SystemExit(0)
