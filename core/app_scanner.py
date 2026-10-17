"""Leitura somente-leitura de aplicativos instalados."""
from dataclasses import dataclass, asdict
import json, os, platform, subprocess

@dataclass
class InstalledApp:
    name: str
    version: str = ""
    publisher: str = ""
    size: str = ""
    date: str = ""
    uninstall: str = ""
    source: str = "registry"

def scan_registry():
    if os.name != "nt": return []
    import winreg
    roots = [(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
             (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
             (winreg.HKEY_CURRENT_USER, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall")]
    out, seen = [], set()
    for root, path in roots:
        try: key = winreg.OpenKey(root, path)
        except OSError: continue
        with key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    with winreg.OpenKey(key, winreg.EnumKey(key, i)) as item:
                        name = winreg.QueryValueEx(item, "DisplayName")[0]
                        if not name or name in seen: continue
                        seen.add(name)
                        def val(k):
                            try: return str(winreg.QueryValueEx(item, k)[0])
                            except OSError: return ""
                        out.append(InstalledApp(name, val("DisplayVersion"), val("Publisher"), val("EstimatedSize"), val("InstallDate"), val("UninstallString")))
                except (OSError, TypeError): continue
    return sorted(out, key=lambda x: x.name.lower())

def scan_store():
    if os.name != "nt": return []
    try:
        p = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-AppxPackage | Select Name,Version,Publisher | ConvertTo-Json -Compress"], capture_output=True, text=True, timeout=20)
        data = json.loads(p.stdout or "[]"); data = data if isinstance(data, list) else [data]
        return [InstalledApp(str(x.get("Name", "")), str(x.get("Version", "")), str(x.get("Publisher", "")), source="store") for x in data if x.get("Name")]
    except Exception: return []

def scan_apps():
    items = scan_registry() + scan_store(); seen=set(); result=[]
    for x in items:
        if x.name.lower() not in seen: seen.add(x.name.lower()); result.append(x)
    return result

def system_snapshot():
    import psutil
    vm=psutil.virtual_memory(); disk=psutil.disk_usage(os.environ.get("SystemDrive", "/")); boot=psutil.boot_time()
    import datetime
    return {"host": platform.node(), "user": os.environ.get("USERNAME", os.environ.get("USER", "")), "windows": platform.platform(), "arch": platform.machine(), "cpu": platform.processor() or "N/D", "cores": psutil.cpu_count(), "cpu_percent": psutil.cpu_percent(), "ram_total": vm.total, "ram_used": vm.used, "ram_percent": vm.percent, "disk_total": disk.total, "disk_used": disk.used, "disk_percent": disk.percent, "uptime": str(datetime.timedelta(seconds=int(datetime.datetime.now().timestamp()-boot)))}

def export_apps(path):
    with open(path, "w", encoding="utf-8") as f: json.dump([asdict(x) for x in scan_apps()], f, ensure_ascii=False, indent=2)
