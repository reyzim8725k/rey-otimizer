"""Interface principal do Rey Optimizer."""
import csv, json, os, platform, threading, time
from pathlib import Path
try:
    import customtkinter as ctk
except ImportError:
    import tkinter as ctk
from tkinter import messagebox, filedialog
from core.logger import AppLogger
from core.app_scanner import scan_apps, system_snapshot
from core.monitor_engine import snapshot
from core import optimizer_engine, uninstaller_engine

BG="#1a1a2e"; PANEL="#16213e"; ACCENT="#8b5cf6"; TEXT="#e5e7eb"
class ReyOptimizerApp:
    def __init__(self):
        self.logger=AppLogger(); self.apps=[]; self.monitoring=True
        ctk.set_appearance_mode("dark") if hasattr(ctk,"set_appearance_mode") else None
        ctk.set_default_color_theme("dark-blue") if hasattr(ctk,"set_default_color_theme") else None
        self.root=ctk.CTk() if hasattr(ctk,"CTk") else ctk.Tk(); self.root.title("Rey Optimizer"); self.root.geometry("1280x800"); self.root.configure(bg=BG)
        icon=Path(__file__).resolve().parent.parent / "assets" / "rey-optimizer.ico"
        if icon.exists():
            try: self.root.iconbitmap(str(icon))
            except Exception: pass
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.build(); self.show_dashboard(); self.refresh_metrics(); self.refresh_apps()
    def button(self, parent, text, command): return ctk.CTkButton(parent,text=text,command=command,fg_color=ACCENT,hover_color="#7c3aed")
    def build(self):
        self.side=ctk.CTkFrame(self.root,width=220,fg_color=PANEL); self.side.pack(side="left",fill="y",padx=10,pady=10)
        ctk.CTkLabel(self.side,text="🛡️ Rey Optimizer",font=("Arial",22,"bold")).pack(pady=(25,8)); ctk.CTkLabel(self.side,text="ADMIN / modo seguro",text_color="#10b981").pack(pady=(0,25))
        for text, fn in [("🏠 Dashboard",self.show_dashboard),("📦 Desinstalador",self.show_uninstaller),("⚡ Otimização",self.show_optimizer),("📊 Monitoramento",self.show_monitor),("📝 Logs",self.show_logs),("⚙️ Configurações",self.show_settings)]: self.button(self.side,text,fn).pack(fill="x",pady=5)
        self.content=ctk.CTkFrame(self.root,fg_color=BG); self.content.pack(side="left",fill="both",expand=True,padx=(0,10),pady=10)
    def clear(self):
        for w in self.content.winfo_children(): w.destroy()
    def title(self,text): ctk.CTkLabel(self.content,text=text,font=("Arial",28,"bold"),text_color=TEXT).pack(anchor="w",padx=24,pady=(18,12))
    def show_dashboard(self):
        self.clear(); self.title("Dashboard")
        self.info=ctk.CTkTextbox(self.content,height=250); self.info.pack(fill="x",padx=24); self.button(self.content,"🔍 Escanear sistema",self.refresh_metrics).pack(anchor="w",padx=24,pady=14)
        self.chart=ctk.CTkTextbox(self.content); self.chart.pack(fill="both",expand=True,padx=24,pady=5)
    def refresh_metrics(self):
        try:
            s=system_snapshot(); text="\n".join(f"{k}: {v}" for k,v in s.items());
            if hasattr(self,"info"): self.info.delete("1.0","end"); self.info.insert("end",text)
        except Exception as e: self.logger.error("dashboard","snapshot",str(e))
        if self.monitoring: self.root.after(1000,self.refresh_metrics)
    def refresh_apps(self):
        def work():
            try: self.apps=scan_apps(); self.logger.success("scanner","scan",f"{len(self.apps)} aplicativos")
            except Exception as e: self.logger.error("scanner","scan",str(e))
        threading.Thread(target=work,daemon=True).start()
    def show_uninstaller(self):
        self.clear(); self.title("Desinstalador"); top=ctk.CTkFrame(self.content,fg_color=BG); top.pack(fill="x",padx=24)
        self.search=ctk.CTkEntry(top,placeholder_text="Filtrar aplicativos..."); self.search.pack(side="left",fill="x",expand=True,padx=5); self.search.bind("<KeyRelease>",lambda e:self.render_apps())
        self.button(top,"Recarregar",self.refresh_apps).pack(side="left",padx=5); self.button(top,"Desinstalar selecionados",self.uninstall_selected).pack(side="left",padx=5)
        self.appbox=ctk.CTkScrollableFrame(self.content,fg_color=PANEL); self.appbox.pack(fill="both",expand=True,padx=24,pady=12); self.vars=[]; self.render_apps()
    def render_apps(self):
        if not hasattr(self,"appbox"): return
        for w in self.appbox.winfo_children(): w.destroy()
        q=self.search.get().lower() if hasattr(self,"search") else ""
        self.vars=[]
        for app in self.apps:
            if q and q not in app.name.lower(): continue
            var=ctk.BooleanVar(); self.vars.append((var,app)); ctk.CTkCheckBox(self.appbox,text=f"{app.name} | {app.version} | {app.publisher}",variable=var).pack(anchor="w",pady=3)
    def uninstall_selected(self):
        selected=[a for v,a in self.vars if v.get()]
        if not selected: return messagebox.showinfo("Rey Optimizer","Selecione pelo menos um aplicativo.")
        names="\n".join(a.name for a in selected)
        if not messagebox.askyesno("Confirmar remoção",f"A ação é destrutiva e será executada pelos desinstaladores oficiais:\n\n{names}\n\nContinuar?"): return
        def work():
            for app in selected:
                try: r=uninstaller_engine.uninstall(app); self.logger.success("uninstaller",app.name,f"returncode={r.returncode}")
                except Exception as e: self.logger.error("uninstaller",app.name,str(e))
            self.root.after(0,self.refresh_apps)
        threading.Thread(target=work,daemon=True).start()
    def show_optimizer(self):
        self.clear(); self.title("Otimização segura"); ctk.CTkLabel(self.content,text="Cada ação exige confirmação. Recomenda-se ponto de restauração antes de alterações.",text_color="#f59e0b").pack(anchor="w",padx=24)
        for name, fn, desc in [("Limpar arquivos temporários",optimizer_engine.clean_temp,"Remove somente arquivos da pasta TEMP do usuário."),("Limpar cache DNS",optimizer_engine.flush_dns,"Executa ipconfig /flushdns."),("Criar ponto de restauração",optimizer_engine.system_restore_point,"Solicita ao Windows um ponto de restauração.")]:
            f=ctk.CTkFrame(self.content,fg_color=PANEL); f.pack(fill="x",padx=24,pady=8); ctk.CTkLabel(f,text=f"{name}\n{desc}",justify="left").pack(side="left",padx=12,pady=10); self.button(f,"Aplicar",lambda fn=fn,name=name:self.apply_optimizer(name,fn)).pack(side="right",padx=12)
    def apply_optimizer(self,name,fn):
        if not messagebox.askyesno("Confirmar",f"Executar: {name}? Isso pode alterar o sistema."): return
        def work():
            try: r=fn(); self.logger.success("optimizer",name,str(r)); self.root.after(0,lambda:messagebox.showinfo("Concluído",f"{name} concluído."))
            except Exception as e: self.logger.error("optimizer",name,str(e)); self.root.after(0,lambda:messagebox.showerror("Erro",str(e)))
        threading.Thread(target=work,daemon=True).start()
    def show_monitor(self):
        self.clear(); self.title("Monitoramento"); self.mon=ctk.CTkTextbox(self.content); self.mon.pack(fill="both",expand=True,padx=24,pady=12); self.update_monitor()
    def update_monitor(self):
        if not hasattr(self,"mon") or not self.mon.winfo_exists(): return
        try: self.mon.delete("1.0","end"); self.mon.insert("end",json.dumps(snapshot(),ensure_ascii=False,indent=2,default=str))
        except Exception as e: self.mon.insert("end",str(e))
        self.root.after(1500,self.update_monitor)
    def show_logs(self):
        self.clear(); self.title("Logs"); box=ctk.CTkTextbox(self.content); box.pack(fill="both",expand=True,padx=24,pady=12); box.insert("end",self.logger.path.read_text(encoding="utf-8") if self.logger.path.exists() else "Sem logs.")
    def show_settings(self):
        self.clear(); self.title("Configurações"); ctk.CTkLabel(self.content,text="Rey Optimizer v1.0\nTema roxo escuro\nAs operações destrutivas sempre pedem confirmação.\nUse em máquina virtual ou com backup quando possível.",justify="left").pack(anchor="w",padx=24,pady=12)
    def run(self): self.root.mainloop()
    def close(self): self.monitoring=False; self.root.destroy()
