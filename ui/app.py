"""Interface visual do Rey Optimizer."""
import json, os, threading, time
from pathlib import Path
from tkinter import messagebox
try:
    import customtkinter as ctk
except ImportError:
    import tkinter as ctk
try:
    from PIL import Image
except ImportError:
    Image = None
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from core.logger import AppLogger
from core.app_scanner import scan_apps, system_snapshot
from core.monitor_engine import snapshot
from core import optimizer_engine, uninstaller_engine

BG = "#1a1a2e"; PANEL = "#16213e"; PANEL_2 = "#1e1e2e"; ACCENT = "#8b5cf6"; TEXT = "#e5e7eb"


def human_size(value):
    """Converte bytes ou kilobytes do Registro para uma unidade legível."""
    try:
        value = float(value)
        if value < 1024 * 1024:  # valores do Registro são normalmente KB
            value *= 1024
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if value < 1024 or unit == "TB":
                return f"{value:.1f} {unit}"
            value /= 1024
    except (TypeError, ValueError):
        return "N/D"


class ReyOptimizerApp:
    def __init__(self):
        self.logger = AppLogger(); self.apps = []; self.monitoring = True
        self.history = {"CPU": [], "RAM": [], "Disco": [], "Rede": []}
        ctk.set_appearance_mode("dark") if hasattr(ctk, "set_appearance_mode") else None
        ctk.set_default_color_theme("dark-blue") if hasattr(ctk, "set_default_color_theme") else None
        self.root = ctk.CTk() if hasattr(ctk, "CTk") else ctk.Tk()
        self.root.title("Rey Optimizer"); self.root.geometry("1320x850"); self.root.minsize(1050, 680); self.root.configure(bg=BG)
        icon = Path(__file__).resolve().parent.parent / "assets" / "rey-optimizer.ico"
        if icon.exists():
            try: self.root.iconbitmap(str(icon))
            except Exception: pass
        self.logo = None
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "rey-optimizer-logo.png"
        if Image and logo_path.exists() and hasattr(ctk, "CTkImage"):
            try: self.logo = ctk.CTkImage(light_image=Image.open(logo_path), dark_image=Image.open(logo_path), size=(30, 30))
            except Exception: pass
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.build(); self.show_dashboard(); self.refresh_metrics(); self.refresh_apps()

    def button(self, parent, text, command):
        return ctk.CTkButton(parent, text=text, command=command, fg_color=ACCENT, hover_color="#7c3aed", corner_radius=10)

    def build(self):
        self.side = ctk.CTkFrame(self.root, width=230, fg_color=PANEL, corner_radius=16); self.side.pack(side="left", fill="y", padx=10, pady=10)
        if self.logo: ctk.CTkLabel(self.side, text="", image=self.logo).pack(pady=(20, 4))
        ctk.CTkLabel(self.side, text="Rey Optimizer", font=("Arial", 22, "bold")).pack(pady=(0, 7))
        ctk.CTkLabel(self.side, text="PAINEL WINDOWS", text_color="#a78bfa", font=("Arial", 11, "bold")).pack(pady=(0, 25))
        for text, fn in [("🏠  Dashboard", self.show_dashboard), ("📦  Desinstalador", self.show_uninstaller), ("⚡  Otimização", self.show_optimizer), ("📊  Monitoramento", self.show_monitor), ("📝  Logs", self.show_logs), ("⚙️  Configurações", self.show_settings)]:
            self.button(self.side, text, fn).pack(fill="x", padx=12, pady=5)
        self.content = ctk.CTkFrame(self.root, fg_color=BG, corner_radius=16); self.content.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

    def clear(self):
        for widget in self.content.winfo_children(): widget.destroy()

    def title(self, text, subtitle=""):
        ctk.CTkLabel(self.content, text=text, font=("Arial", 28, "bold"), text_color=TEXT).pack(anchor="w", padx=26, pady=(20, 2))
        if subtitle: ctk.CTkLabel(self.content, text=subtitle, text_color="#9ca3af").pack(anchor="w", padx=27, pady=(0, 12))

    def metric_card(self, parent, name, value, color=ACCENT):
        card = ctk.CTkFrame(parent, fg_color=PANEL_2, corner_radius=14); card.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(card, text=name, text_color="#9ca3af", font=("Arial", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 0))
        label = ctk.CTkLabel(card, text=value, text_color=color, font=("Arial", 25, "bold")); label.pack(anchor="w", padx=14, pady=(3, 12))
        bar = ctk.CTkProgressBar(card, height=9, progress_color=color); bar.pack(fill="x", padx=14, pady=(0, 14)); bar.set(0)
        return label, bar

    def show_dashboard(self):
        self.clear(); self.title("Dashboard", "Visão geral do desempenho do seu computador")
        self.dashboard_cards = ctk.CTkFrame(self.content, fg_color=BG); self.dashboard_cards.pack(fill="x", padx=20, pady=4)
        self.d_cpu = self.metric_card(self.dashboard_cards, "CPU", "--", "#a78bfa"); self.d_ram = self.metric_card(self.dashboard_cards, "RAM", "--", "#22d3ee"); self.d_disk = self.metric_card(self.dashboard_cards, "DISCO C:", "--", "#f59e0b"); self.d_net = self.metric_card(self.dashboard_cards, "STATUS", "ONLINE", "#10b981")
        self.info = ctk.CTkTextbox(self.content, height=205, fg_color=PANEL, corner_radius=14); self.info.pack(fill="x", padx=26, pady=(16, 8)); self.button(self.content, "🔍  Escanear sistema", self.refresh_metrics).pack(anchor="w", padx=26, pady=8)

    def refresh_metrics(self):
        try:
            s = system_snapshot()
            if hasattr(self, "info"):
                self.info.delete("1.0", "end"); self.info.insert("end", "\n".join([f"  {k.upper():<14} {v}" for k, v in s.items()]))
            for (label, bar), key, source in [(self.d_cpu, "CPU", "cpu_percent"), (self.d_ram, "RAM", "ram_percent"), (self.d_disk, "DISCO C:", "disk_percent")]:
                label.configure(text=f"{s[source]:.0f}%"); bar.set(float(s[source]) / 100)
        except Exception as exc: self.logger.error("dashboard", "snapshot", str(exc))
        if self.monitoring: self.root.after(1000, self.refresh_metrics)

    def refresh_apps(self):
        def work():
            try: self.apps = scan_apps(); self.logger.success("scanner", "scan", f"{len(self.apps)} aplicativos"); self.root.after(0, self.render_apps)
            except Exception as exc: self.logger.error("scanner", "scan", str(exc))
        threading.Thread(target=work, daemon=True).start()

    def show_uninstaller(self):
        self.clear(); self.title("Desinstalador", "Selecione aplicativos para remover usando o desinstalador oficial")
        top = ctk.CTkFrame(self.content, fg_color=BG); top.pack(fill="x", padx=26)
        self.search = ctk.CTkEntry(top, placeholder_text="🔎  Filtrar por nome ou editor..."); self.search.pack(side="left", fill="x", expand=True, padx=(0, 8)); self.search.bind("<KeyRelease>", lambda _: self.render_apps())
        self.button(top, "↻ Recarregar", self.refresh_apps).pack(side="left", padx=4); self.button(top, "🗑️ Desinstalar selecionados", self.uninstall_selected).pack(side="left", padx=4)
        self.appbox = ctk.CTkScrollableFrame(self.content, fg_color=PANEL, corner_radius=14); self.appbox.pack(fill="both", expand=True, padx=26, pady=14); self.vars = []; self.render_apps()

    def render_apps(self):
        if not hasattr(self, "appbox"): return
        for widget in self.appbox.winfo_children(): widget.destroy()
        query = self.search.get().lower() if hasattr(self, "search") else ""; self.vars = []
        header = ctk.CTkFrame(self.appbox, fg_color="#252446"); header.pack(fill="x", pady=(0, 8)); ctk.CTkLabel(header, text="Ícone", width=60).pack(side="left", padx=8); ctk.CTkLabel(header, text="Aplicativo", anchor="w").pack(side="left", fill="x", expand=True); ctk.CTkLabel(header, text="Tamanho", width=110).pack(side="right", padx=8); ctk.CTkLabel(header, text="Versão / Editor", width=220, anchor="w").pack(side="right", padx=8)
        for app in self.apps:
            haystack = f"{app.name} {app.publisher}".lower()
            if query and query not in haystack: continue
            row = ctk.CTkFrame(self.appbox, fg_color=PANEL_2, corner_radius=10); row.pack(fill="x", pady=3); var = ctk.BooleanVar(); self.vars.append((var, app))
            ctk.CTkCheckBox(row, text="", width=30, variable=var).pack(side="left", padx=(8, 2))
            if self.logo: ctk.CTkLabel(row, text="", image=self.logo).pack(side="left", padx=5)
            name = ctk.CTkLabel(row, text=app.name, anchor="w", font=("Arial", 13, "bold")); name.pack(side="left", fill="x", expand=True, padx=8, pady=10)
            ctk.CTkLabel(row, text=human_size(app.size), width=110, text_color="#fbbf24").pack(side="right", padx=8)
            ctk.CTkLabel(row, text=f"{app.version or 'N/D'}\n{app.publisher or 'Editor desconhecido'}", width=220, anchor="w", text_color="#9ca3af").pack(side="right", padx=8)
        if not self.apps: ctk.CTkLabel(self.appbox, text="Nenhum aplicativo carregado. Clique em Recarregar.", text_color="#9ca3af").pack(pady=30)

    def uninstall_selected(self):
        selected = [app for var, app in self.vars if var.get()]
        if not selected: return messagebox.showinfo("Rey Optimizer", "Selecione pelo menos um aplicativo.")
        names = "\n".join(f"• {app.name} — {human_size(app.size)}" for app in selected)
        if not messagebox.askyesno("Confirmar remoção", f"A remoção será feita pelos desinstaladores oficiais:\n\n{names}\n\nContinuar?"): return
        def work():
            for app in selected:
                try: result = uninstaller_engine.uninstall(app); self.logger.success("uninstaller", app.name, f"returncode={result.returncode}")
                except Exception as exc: self.logger.error("uninstaller", app.name, str(exc))
            self.root.after(0, self.refresh_apps)
        threading.Thread(target=work, daemon=True).start()

    def show_optimizer(self):
        self.clear(); self.title("Otimização segura", "Ações críticas exigem confirmação explícita"); ctk.CTkLabel(self.content, text="Recomendação: crie um ponto de restauração antes de alterar o sistema.", text_color="#f59e0b").pack(anchor="w", padx=26)
        for name, fn, desc in [("Limpar arquivos temporários", optimizer_engine.clean_temp, "Remove somente arquivos da pasta TEMP."), ("Limpar cache DNS", optimizer_engine.flush_dns, "Executa ipconfig /flushdns."), ("Criar ponto de restauração", optimizer_engine.system_restore_point, "Solicita um ponto de restauração ao Windows.")]:
            frame = ctk.CTkFrame(self.content, fg_color=PANEL, corner_radius=12); frame.pack(fill="x", padx=26, pady=8); ctk.CTkLabel(frame, text=f"{name}\n{desc}", justify="left").pack(side="left", padx=14, pady=13); self.button(frame, "Aplicar", lambda fn=fn, name=name: self.apply_optimizer(name, fn)).pack(side="right", padx=14)

    def apply_optimizer(self, name, fn):
        if not messagebox.askyesno("Confirmar", f"Executar: {name}? Isso pode alterar o sistema."): return
        def work():
            try: result = fn(); self.logger.success("optimizer", name, str(result)); self.root.after(0, lambda: messagebox.showinfo("Concluído", f"{name} concluído."))
            except Exception as exc: self.logger.error("optimizer", name, str(exc)); self.root.after(0, lambda: messagebox.showerror("Erro", str(exc)))
        threading.Thread(target=work, daemon=True).start()

    def show_monitor(self):
        self.clear(); self.title("Monitoramento em tempo real", "Atualização automática a cada 1,5 segundos")
        self.monitor_cards = ctk.CTkFrame(self.content, fg_color=BG); self.monitor_cards.pack(fill="x", padx=20, pady=3)
        self.m_cpu = self.metric_card(self.monitor_cards, "CPU TOTAL", "0%", "#a78bfa"); self.m_ram = self.metric_card(self.monitor_cards, "RAM USADA", "0%", "#22d3ee"); self.m_disk = self.metric_card(self.monitor_cards, "DISCO I/O", "0 MB/s", "#f59e0b"); self.m_net = self.metric_card(self.monitor_cards, "REDE", "ativa", "#10b981")
        if HAS_MPL:
            self.figure = Figure(figsize=(8, 4.3), dpi=100, facecolor=BG); self.axes = self.figure.subplots(2, 2); self.figure.subplots_adjust(hspace=.45, wspace=.25, left=.08, right=.97, top=.91, bottom=.12)
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.content); self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=22, pady=8)
        self.mon_text = ctk.CTkTextbox(self.content, height=120, fg_color=PANEL, corner_radius=12); self.mon_text.pack(fill="x", padx=26, pady=(0, 12)); self.update_monitor()

    def update_monitor(self):
        if not hasattr(self, "mon_text") or not self.mon_text.winfo_exists(): return
        try:
            data = snapshot(); cpu = float(data["cpu"]); ram = float(data["ram"]); read = data["disk_read"] / 1024 / 1024; down = data["down"] / 1024 / 1024
            for key, value in [("CPU", cpu), ("RAM", ram), ("Disco", read), ("Rede", down)]:
                self.history[key].append(value); self.history[key] = self.history[key][-45:]
            self.m_cpu[0].configure(text=f"{cpu:.0f}%"); self.m_cpu[1].set(cpu / 100); self.m_ram[0].configure(text=f"{ram:.0f}%"); self.m_ram[1].set(ram / 100); self.m_disk[0].configure(text=f"{read:.1f} MB"); self.m_net[0].configure(text="conectada")
            self.mon_text.delete("1.0", "end"); self.mon_text.insert("end", "TOP CPU\n" + "\n".join(f"  {p.get('name','N/D')}  {p.get('cpu_percent',0):.1f}%" for p in data["top_cpu"][:5]))
            if HAS_MPL:
                colors = ["#a78bfa", "#22d3ee", "#f59e0b", "#10b981"]
                for ax, (key, color) in zip(self.axes.flat, [("CPU", colors[0]), ("RAM", colors[1]), ("Disco", colors[2]), ("Rede", colors[3])]):
                    ax.clear(); ax.plot(self.history[key], color=color, linewidth=2.2); ax.fill_between(range(len(self.history[key])), self.history[key], color=color, alpha=.12); ax.set_title(key, color="white", fontsize=10, loc="left"); ax.tick_params(colors="#9ca3af", labelsize=8); ax.set_facecolor(PANEL_2); ax.grid(alpha=.12, color="white"); [spine.set_color("#3b3562") for spine in ax.spines.values()]
                self.canvas.draw_idle()
        except Exception as exc: self.logger.error("monitor", "snapshot", str(exc))
        self.root.after(1500, self.update_monitor)

    def show_logs(self):
        self.clear(); self.title("Logs", "Histórico de operações e eventos"); box = ctk.CTkTextbox(self.content, fg_color=PANEL, corner_radius=14); box.pack(fill="both", expand=True, padx=26, pady=12); box.insert("end", self.logger.path.read_text(encoding="utf-8") if self.logger.path.exists() else "Sem logs.")

    def show_settings(self):
        self.clear(); self.title("Configurações"); ctk.CTkLabel(self.content, text="Rey Optimizer v1.0\nTema roxo escuro\nMonitoramento com gráficos matplotlib\nAs operações destrutivas sempre pedem confirmação.\nUse em máquina virtual ou com backup quando possível.", justify="left").pack(anchor="w", padx=26, pady=12)

    def run(self): self.root.mainloop()
    def close(self): self.monitoring = False; self.root.destroy()
