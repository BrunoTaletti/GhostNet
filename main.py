import os
import sys
import json
import threading
import requests
import customtkinter as ctk
from PIL import Image
from packaging import version

# Configurações do App
APP_NAME = "GhostNet"
GITHUB_REPO = "BrunoTaletti/GhostNet" 
DEFAULT_VERSION = "1.0.0"

# Configuração de caminhos (AppData)
APPDATA_DIR = os.path.join(os.getenv('APPDATA'), APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(APPDATA_DIR, "ip_history.log")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")

# Estilo Dithering/Terminal
BG_COLOR = "#050505"
TEXT_COLOR = "#E0E0E0"
ACCENT_COLOR = "#404040"
FONT_PRIMARY = ("Consolas", 12)
FONT_BOLD = ("Consolas", 12, "bold")
FONT_TITLE = ("Consolas", 14, "bold")

ctk.set_appearance_mode("dark")

class GhostNetApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Carregar Versão primeiro
        self.current_version = self.load_version_file()

        self.title(f"GhostNet - {self.current_version}")
        self.configure(fg_color=BG_COLOR)
        
        # Geometria Inicial
        self.geometry("380x450")
        self.minsize(350, 280)
        
        # Tentar carregar ícone sem crashar
        try:
            icon_path = self.get_path("app-icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass

        # Estado
        self.history = self.load_ip_history()
        self.config_data = self.load_config()
        self.hud_var = ctk.BooleanVar(value=self.config_data.get("show_hud", True))
        
        self.setup_ui()
        self.toggle_hud() # Ajusta o tamanho inicial baseado na preferência
        
        # Iniciar rotinas de fundo
        threading.Thread(target=self.check_update, daemon=True).start()
        self.reload_ip()

    def get_path(self, relative_path):
        """ Retorna caminho absoluto para recursos (Dev vs PyInstaller) """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_version_file(self):
        try:
            v_path = self.get_path("version.txt")
            if os.path.exists(v_path):
                with open(v_path, "r") as f:
                    return f.read().strip()
        except:
            pass
        return DEFAULT_VERSION

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"show_hud": True}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"show_hud": self.hud_var.get()}, f)

    def load_ip_history(self):
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return []

    def save_ip(self, ip):
        if ip not in self.history:
            self.history.append(ip)
            with open(HISTORY_FILE, 'a') as f:
                f.write(f"{ip}\n")
            self.update_hud_text()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # 1. Logo
        logo_path = self.get_path("app-logo.png")
        if os.path.exists(logo_path):
            try:
                self.logo_img = ctk.CTkImage(
                    light_image=Image.open(logo_path), 
                    dark_image=Image.open(logo_path), 
                    size=(400, 140)
                )
                self.lbl_logo = ctk.CTkLabel(self, image=self.logo_img, text="", fg_color=BG_COLOR)
            except:
                self.lbl_logo = ctk.CTkLabel(self, text="[ GHOSTNET ]", font=("Consolas", 24, "bold"))
        else:
            self.lbl_logo = ctk.CTkLabel(self, text="[ GHOSTNET ]", font=("Consolas", 24, "bold"))
        
        self.lbl_logo.grid(row=0, column=0, pady=(15, 10))

        # 2. Status
        self.frame_status = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.frame_status.grid(row=1, column=0, padx=20, sticky="ew")
        self.frame_status.grid_columnconfigure(0, weight=1)

        self.lbl_ip = ctk.CTkLabel(self.frame_status, text="---.---.---.---", font=FONT_TITLE)
        self.lbl_ip.grid(row=0, column=0, pady=(5, 0))

        self.lbl_status = ctk.CTkLabel(self.frame_status, text="Aguardando...", font=FONT_PRIMARY)
        self.lbl_status.grid(row=1, column=0, pady=(0, 10))

        self.btn_reload = ctk.CTkButton(
            self.frame_status, text="[ ROTACIONAR IP ]", font=FONT_BOLD, 
            fg_color=BG_COLOR, border_width=1, border_color=TEXT_COLOR, 
            hover_color=ACCENT_COLOR, command=self.reload_ip
        )
        self.btn_reload.grid(row=2, column=0, pady=5, sticky="ew")

        # 3. Checkbox
        self.chk_hud = ctk.CTkCheckBox(
            self, text="Exibir Logs (HUD)", font=FONT_PRIMARY, 
            variable=self.hud_var, command=self.toggle_hud,
            fg_color=TEXT_COLOR, border_color=TEXT_COLOR, hover_color=ACCENT_COLOR
        )
        self.chk_hud.grid(row=2, column=0, pady=10, padx=25, sticky="w")

        # 4. HUD Textbox
        self.hud_textbox = ctk.CTkTextbox(
            self, font=("Consolas", 11), fg_color="#0A0A0A", text_color="#888888", 
            border_width=1, border_color="#222222", corner_radius=0
        )

        # 5. Footer (Rodapé)
        self.frame_footer = ctk.CTkFrame(self, fg_color=BG_COLOR, height=25, corner_radius=0)
        self.frame_footer.grid(row=4, column=0, sticky="ew", padx=10, pady=2)
        
        self.frame_footer.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.spacer = ctk.CTkLabel(self.frame_footer, text="")
        self.spacer.grid(row=0, column=0)

        self.lbl_version_val = ctk.CTkLabel(self.frame_footer, text=f"v{self.current_version}", 
                                           font=("Consolas", 9), text_color="#444444")
        self.lbl_version_val.grid(row=0, column=1, sticky="n") # "n" centraliza horizontalmente por padrão

        self.lbl_upd_status = ctk.CTkLabel(self.frame_footer, text="", 
                                           font=("Consolas", 9), text_color="#444444")
        self.lbl_upd_status.grid(row=0, column=2, sticky="e")

    def toggle_hud(self):
        self.save_config()
        if self.hud_var.get():
            self.hud_textbox.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="nsew")
            self.geometry("380x450")
            self.update_hud_text()
        else:
            self.hud_textbox.grid_forget()
            self.geometry("380x250")

    def update_hud_text(self):
        self.hud_textbox.configure(state="normal")
        self.hud_textbox.delete("1.0", "end")
        if not self.history:
            self.hud_textbox.insert("end", "> Nenhum log.")
        else:
            for ip in reversed(self.history[-20:]):
                self.hud_textbox.insert("end", f" [LOG] {ip}\n")
        self.hud_textbox.configure(state="disabled")

    def reload_ip(self):
        self.lbl_status.configure(text="Sincronizando...", text_color=TEXT_COLOR)
        self.btn_reload.configure(state="disabled")
        threading.Thread(target=self._fetch_ip, daemon=True).start()

    def _fetch_ip(self):
        try:
            res = requests.get('https://api.ipify.org', timeout=5).text.strip()
            self.lbl_ip.configure(text=res)
            if res in self.history:
                self.lbl_status.configure(text="ALERTA: IP REPETIDO", text_color="#FF4444")
            else:
                self.lbl_status.configure(text="CONEXÃO SEGURA", text_color="#44FF44")
                self.save_ip(res)
        except:
            self.lbl_ip.configure(text="ERRO")
            self.lbl_status.configure(text="SEM CONEXÃO", text_color="#FF4444")
        
        self.btn_reload.configure(state="normal")

    def check_update(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            r = requests.get(url, timeout=5).json()
            remote_v = r.get("tag_name", "").replace("v", "")
            if remote_v and version.parse(remote_v) > version.parse(self.current_version):
                self.lbl_upd_status.configure(text="Update Disponível", text_color="#44FF44")
        except:
            pass

if __name__ == "__main__":
    app = GhostNetApp()
    app.mainloop()