import os
import sys
import json
import requests
from packaging import version
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QCheckBox, 
                             QTextEdit, QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont, QCursor, QTextCursor

# ==========================================
# CONFIGURAÇÕES DO APP
# ==========================================
APP_NAME = "GhostNet"
GITHUB_REPO = "BrunoTaletti/GhostNet" 
DEFAULT_VERSION = "1.0.0"

APPDATA_DIR = os.path.join(os.getenv('APPDATA'), APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(APPDATA_DIR, "ip_history.log")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_current_version():
    v_path = resource_path("version.txt")
    if os.path.exists(v_path):
        with open(v_path, "r") as f:
            return f.read().strip()
    return DEFAULT_VERSION

# ==========================================
# THREADS DE OPERAÇÃO
# ==========================================
class UpdateChecker(QThread):
    update_available = pyqtSignal(str)
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version

    def run(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            r = requests.get(url, timeout=5).json()
            remote_v = r.get("tag_name", "").replace("v", "")
            if remote_v and version.parse(remote_v) > version.parse(self.current_version):
                self.update_available.emit(remote_v)
        except: pass

class IpFetcher(QThread):
    result_signal = pyqtSignal(str, bool)
    def run(self):
        try:
            res = requests.get('https://api.ipify.org', timeout=5).text.strip()
            self.result_signal.emit(res, False)
        except: self.result_signal.emit("ERRO_CONEXÃO", True)

# ==========================================
# INTERFACE PRINCIPAL (UI FLUIDA)
# ==========================================
class GhostNetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_version = get_current_version()
        self.history = self.load_ip_history()
        self.config_data = self.load_config()
        self.show_hud = self.config_data.get("show_hud", True)
        self.old_pos = None

        self.init_ui()
        self.apply_hud_state()
        
        self.update_thread = UpdateChecker(self.current_version)
        self.update_thread.update_available.connect(self.on_update_available)
        self.update_thread.start()
        
        self.ip_fetcher = IpFetcher()
        self.ip_fetcher.result_signal.connect(self.on_ip_fetched)
        self.reload_ip()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(300, 450)
        
        self.central_widget = QFrame()
        self.central_widget.setObjectName("MainFrame")
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        # ESTILO HACKER / REFERENCIA.PY
        self.setStyleSheet("""
            QFrame#MainFrame {
                background-color: #000000;
                border: 1px solid #C6F91F;
                border-top: 2px solid #C6F91F;
            }
            QLabel { color: #888888; font-family: 'Consolas'; }
            
            /* Top Bar */
            QPushButton#CloseBtn, QPushButton#MinBtn {
                background-color: transparent; color: #444444; font-weight: bold; font-family: 'Consolas'; font-size: 14px;
            }
            QPushButton#CloseBtn:hover { color: #FFFFFF; }
            QPushButton#MinBtn:hover { color: #FFFFFF; }

            /* Botão Rotacionar */
            QPushButton#ActionBtn {
                background-color: #050505; color: #FFFFFF; border: 1px solid #111111;
                border-bottom: 2px solid #333333; padding: 10px; font-family: 'Consolas'; 
                font-weight: bold; font-size: 11px; letter-spacing: 1px;
            }
            QPushButton#ActionBtn:hover { background-color: #0A0A0A; border-bottom: 2px solid #FFFFFF; }
            QPushButton#ActionBtn:disabled { color: #222222; border-bottom: 2px solid #111111; }

            /* HUD Log Estilizado */
            QTextEdit {
                background-color: #050505; 
                color: #FFFFFF; 
                border: 1px solid #111111;
                border-bottom: 2px solid #333333;
                padding: 8px; 
                font-family: 'Consolas';
                font-size: 10px;
                letter-spacing: 1px;
            }
            QScrollBar:vertical { width: 0px; }

            /* Checkbox */
            QCheckBox { color: #555555; font-family: 'Consolas'; font-size: 10px; letter-spacing: 1px; }
            QCheckBox::indicator { width: 12px; height: 12px; background: #050505; border: 1px solid #333333;}
            QCheckBox::indicator:checked { background: #C6F91F;}
            
            /* Versão */
            QPushButton#VersionBtn {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 10px; 
                font-family: 'Consolas'; 
                letter-spacing: 1px;
                margin-top: 15px; /* Adicionado padding/margem no topo */
                margin-bottom: 5px;
            }
            QPushButton#VersionBtn:hover { color: #FFFFFF; }
        """)

        # 1. Title Bar
        title_bar = QFrame()
        title_bar.setFixedHeight(30)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)
        
        title_label = QLabel("GHOST//NET")
        title_label.setStyleSheet("color: #C6F91F; font-weight: bold; font-size: 10px; letter-spacing: 2px;")
        
        min_btn = QPushButton("—")
        min_btn.setObjectName("MinBtn")
        min_btn.setFixedSize(30, 30)
        min_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton("X")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(min_btn)
        title_layout.addWidget(close_btn)
        main_layout.addWidget(title_bar)

        # 2. Content Area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 5, 25, 10)
        content_layout.setSpacing(12)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = resource_path("app-logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(220, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        content_layout.addWidget(self.logo_label)

        # IP Principal (Reduzido para 20pt para não vazar)
        self.lbl_ip = QLabel("000.000.000.000")
        self.lbl_ip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_ip.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        self.lbl_ip.setStyleSheet("color: #FFFFFF; letter-spacing: 0px;")
        content_layout.addWidget(self.lbl_ip)

        # Status Label
        self.lbl_status = QLabel("SYS.INIT //")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        content_layout.addWidget(self.lbl_status)

        # Botão de Ação
        self.btn_reload = QPushButton("SYS.SYNC_IP")
        self.btn_reload.setObjectName("ActionBtn")
        self.btn_reload.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_reload.clicked.connect(self.reload_ip)
        content_layout.addWidget(self.btn_reload)

        # Checkbox HUD
        self.chk_hud = QCheckBox("VIEW_SESSION_LOGS")
        self.chk_hud.setChecked(self.show_hud)
        self.chk_hud.stateChanged.connect(self.toggle_hud)
        content_layout.addWidget(self.chk_hud)

        # HUD Textbox
        self.hud_textbox = QTextEdit()
        self.hud_textbox.setReadOnly(True)
        content_layout.addWidget(self.hud_textbox)

        content_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Footer Versão Centralizado
        self.version_btn = QPushButton(f"SYS.VER // {self.current_version}")
        self.version_btn.setObjectName("VersionBtn")
        content_layout.addWidget(self.version_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(content_widget)

    # ==========================================
    # LOGICA DE PERSISTÊNCIA
    # ==========================================
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: return json.load(f)
            except: pass
        return {"show_hud": True}

    def load_ip_history(self):
        if not os.path.exists(HISTORY_FILE): return []
        try:
            with open(HISTORY_FILE, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except: return []

    def save_ip(self, ip):
        if ip not in self.history:
            self.history.insert(0, ip)
            with open(HISTORY_FILE, 'a') as f: f.write(f"{ip}\n")
            self.update_hud_text()

    # ==========================================
    # LOGICA DE INTERFACE
    # ==========================================
    def toggle_hud(self, state):
        self.show_hud = bool(state)
        with open(CONFIG_FILE, 'w') as f: json.dump({"show_hud": self.show_hud}, f)
        self.apply_hud_state()

    def apply_hud_state(self):
        if self.show_hud:
            self.hud_textbox.setVisible(True)
            self.setFixedSize(300, 490) # Altura com HUD
            self.update_hud_text()
        else:
            self.hud_textbox.setVisible(False)
            self.setFixedSize(300, 300) # Altura sem HUD com respiro para versão

    def update_hud_text(self):
        self.hud_textbox.clear()
        if not self.history:
            self.hud_textbox.append("NO_DATA_LOGGED //")
        else:
            current_ip = self.lbl_ip.text()
            logs = self.history[:100]
            for ip in logs:
                # Adiciona o asterisco se for o IP atual
                marker = '<span style="color: #C6F91F;"> *</span>' if ip == current_ip else ""
                self.hud_textbox.append(f" [LOG] {ip}{marker}")
            
            self.hud_textbox.moveCursor(QTextCursor.MoveOperation.Start)

    def reload_ip(self):
        self.lbl_status.setText("SYS.SYNCING_NETWORK")
        self.lbl_status.setStyleSheet("color: #FFFFFF;")
        self.btn_reload.setEnabled(False)
        self.ip_fetcher.start()

    def on_ip_fetched(self, res, is_error):
        self.lbl_ip.setText(res)
        if is_error:
            self.lbl_status.setText("SYS.CONN_ERROR")
            self.lbl_status.setStyleSheet("color: #D52941;")
        else:
            if res in self.history:
                self.lbl_status.setText("SYS.REPEATED_IP_WARN")
                self.lbl_status.setStyleSheet("color: #D52941;")
                # Atualiza os logs para o asterisco pular para o IP repetido
                self.update_hud_text()
            else:
                self.lbl_status.setText("SYS.SECURE_CONNECTION")
                self.lbl_status.setStyleSheet("color: #00916E;")
                self.save_ip(res)
        self.btn_reload.setEnabled(True)

    def on_update_available(self, v_new):
        self.version_btn.setText(f"SYS.UPDATE_READY // v{v_new}")
        self.version_btn.setStyleSheet("color: #00916E; font-weight: bold;")

    # Mover Janela
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GhostNetApp()
    window.show()
    sys.exit(app.exec())