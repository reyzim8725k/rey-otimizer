"""Coleta de métricas sem bloquear a interface."""
import psutil, time

def snapshot():
    net=psutil.net_io_counters(); disk=psutil.disk_io_counters(); vm=psutil.virtual_memory()
    procs=[]
    for p in psutil.process_iter(["pid","name","memory_percent","cpu_percent"]):
        try: procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied): pass
    return {"cpu": psutil.cpu_percent(), "ram": vm.percent, "disk_read": getattr(disk,"read_bytes",0), "disk_write": getattr(disk,"write_bytes",0), "up": net.bytes_sent, "down": net.bytes_recv, "top_cpu": sorted(procs,key=lambda x:x.get("cpu_percent") or 0,reverse=True)[:10], "top_ram": sorted(procs,key=lambda x:x.get("memory_percent") or 0,reverse=True)[:10]}
