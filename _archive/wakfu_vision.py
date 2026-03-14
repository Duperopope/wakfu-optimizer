# -*- coding: utf-8 -*-
"""Vision Automator v4.0 — Multi-image templates, robust scan, UI fixes"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import ctypes, ctypes.wintypes, json, os, sys, time, threading, shutil, traceback, glob
from datetime import datetime
from collections import Counter
from copy import deepcopy

import win32gui, win32con, win32api, win32ui, win32process  # type: ignore
import psutil
from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFont
import cv2
import numpy as np
import subprocess
import keyboard
import subprocess

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAPTURES_DIR = os.path.join(BASE_DIR, "captures")
LIBRARY_DIR  = os.path.join(BASE_DIR, "library")
LOGS_DIR     = os.path.join(BASE_DIR, "logs")
CONFIG_FILE  = os.path.join(BASE_DIR, "app", "config.json")

for _d in (CAPTURES_DIR, LIBRARY_DIR, LOGS_DIR):
    os.makedirs(_d, exist_ok=True)

DEFAULT_CONFIG = {
    "confidence_threshold": 0.75,
    "scan_interval_ms": 500,
    "action_delay_ms": 300,
    "hover_delay_ms": 150,
    "calibration_offset_x": 0,
    "calibration_offset_y": 0,
    "calibration_points": [],
    "selected_process": "",
    "categories": [],
    "templates": {},
    "sequences": [],
    "name_history": [],
    "grid": {
        "origin_x": 0, "origin_y": 0,
        "cell_w": 43, "cell_h": 22,
        "angle_deg": 27,
        "cols": 20, "rows": 20,
        "visible": False
    },
    "grid_conditions": [],
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
        except:
            pass
    return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════
# VISION
# ═══════════════════════════════════════════════════════════
def capture_window(hwnd):
    try:
        if not win32gui.IsWindow(hwnd):
            return None
        rect = win32gui.GetClientRect(hwnd)
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        if w <= 0 or h <= 0:
            return None
        hwnd_dc  = win32gui.GetWindowDC(hwnd)
        mfc_dc   = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc  = mfc_dc.CreateCompatibleDC()
        bmp      = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(bmp)
        pt    = win32gui.ClientToScreen(hwnd, (0, 0))
        wt    = win32gui.GetWindowRect(hwnd)
        x_off = pt[0] - wt[0]
        y_off = pt[1] - wt[1]
        res   = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)
        if res == 0:
            save_dc.BitBlt((0, 0), (w, h), mfc_dc, (x_off, y_off), win32con.SRCCOPY)
        info = bmp.GetInfo()
        bits = bmp.GetBitmapBits(True)
        img  = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]),
                                bits, "raw", "BGRX", 0, 1)
        win32gui.DeleteObject(bmp.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        return img
    except:
        return None


def pil_to_cv(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def find_template(source_cv, tpl_cv, threshold=0.75):
    if source_cv is None or tpl_cv is None:
        return []
    sh, sw = source_cv.shape[:2]
    th, tw = tpl_cv.shape[:2]
    if th > sh or tw > sw or th < 3 or tw < 3:
        return []
    try:
        result = cv2.matchTemplate(source_cv, tpl_cv, cv2.TM_CCOEFF_NORMED)
    except:
        return []
    locs = np.where(result >= threshold)
    matches = []
    for pt in zip(*locs[::-1]):
        c = float(result[pt[1], pt[0]])
        matches.append((int(pt[0]), int(pt[1]), tw, th, c))
    if not matches:
        return []
    matches.sort(key=lambda m: m[4], reverse=True)
    filtered = []
    for m in matches:
        if not any(abs(m[0]-f[0]) < tw*0.5 and abs(m[1]-f[1]) < th*0.5 for f in filtered):
            filtered.append(m)
    return filtered


def find_template_multi(source_cv, templates_cv, threshold=0.6):
    if source_cv is None or not templates_cv:
        return []
    results = []
    sh, sw = source_cv.shape[:2]
    use_half = sh > 600 and sw > 800
    if use_half:
        small_src = cv2.resize(source_cv, (sw//2, sh//2), interpolation=cv2.INTER_AREA)
    for tpl_cv in templates_cv:
        if use_half:
            th, tw = tpl_cv.shape[:2]
            if th > 12 and tw > 12:
                small_tpl = cv2.resize(tpl_cv, (tw//2, th//2), interpolation=cv2.INTER_AREA)
                pre = find_template(small_src, small_tpl, max(threshold - 0.05, 0.3))
                for px, py, ptw, pth, pc in pre:
                    rx, ry = px*2, py*2
                    margin = 8
                    x1 = max(0, rx-margin);  y1 = max(0, ry-margin)
                    x2 = min(sw, rx+tw+margin); y2 = min(sh, ry+th+margin)
                    roi = source_cv[y1:y2, x1:x2]
                    for sx, sy, stw, sth, sc in find_template(roi, tpl_cv, threshold):
                        results.append((sx+x1, sy+y1, stw, sth, sc))
                continue
        results.extend(find_template(source_cv, tpl_cv, threshold))
    return results


def compare_images_multi(img_cv, template_cv):
    if img_cv is None or template_cv is None:
        return 0.0
    h1, w1 = img_cv.shape[:2]
    h2, w2 = template_cv.shape[:2]
    if h1 != h2 or w1 != w2:
        ratio = max(h1,w1)/max(h2,w2) if max(h2,w2)>0 else 0
        if ratio < 0.5 or ratio > 2.0:
            return 0.0
        template_cv = cv2.resize(template_cv, (w1, h1))
    scores = []
    try:
        res = cv2.matchTemplate(img_cv, template_cv, cv2.TM_CCOEFF_NORMED)
        scores.append(float(res[0][0]))
    except: pass
    try:
        hsv1 = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.cvtColor(template_cv, cv2.COLOR_BGR2HSV)
        h1c  = cv2.calcHist([hsv1],[0,1],None,[50,60],[0,180,0,256])
        h2c  = cv2.calcHist([hsv2],[0,1],None,[50,60],[0,180,0,256])
        cv2.normalize(h1c,h1c,0,1,cv2.NORM_MINMAX)
        cv2.normalize(h2c,h2c,0,1,cv2.NORM_MINMAX)
        scores.append(cv2.compareHist(h1c,h2c,cv2.HISTCMP_CORREL))
    except: pass
    try:
        g1 = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        g2 = cv2.cvtColor(template_cv, cv2.COLOR_BGR2GRAY)
        scores.append(1.0 - np.mean(cv2.absdiff(g1,g2))/255.0)
    except: pass
    return max(scores) if scores else 0.0


# ═══════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════
CATEGORIES = {
    "Grille": [
        "Case vide","Case obstacle","Case mur","Bord de map",
        "Case survolée","Case occupée joueur","Case occupée allié",
        "Case occupée ennemi","Case occupée monstre",
    ],
    "Monstre":     ["Vivant","Mort"],
    "Objet":       ["Amulette","Casque","Cape","Plastron","Ceinture",
                    "Bottes","Anneau","Arme","Bouclier","Familier","Emblème"],
    "Personnage":  ["Héros","Joueur contrôlé","Allié","Joueur ennemi"],
    "Ressource":   ["Herboristerie","Minage","Bûcheron","Pêche","Paysan","Trappeur"],
    "Interface":   [],
    "Action":      [],
    "Événement":   [],
    "Quête":       [],
    "Arène":       [],
}
CATEGORY_LIST = list(CATEGORIES.keys())

WAKFU_CLASSES = [
    "Féca","Osamodas","Enutrof","Sram","Xélor","Ecaflip","Eniripsa","Iop","Crâ",
    "Sadida","Sacrieur","Pandawa","Roublard","Zobal","Steamer","Eliotrope",
    "Huppermage","Ouginak","Forgelance",
]
ALLY_SUBTYPES  = ["Tout"] + WAKFU_CLASSES
ENEMY_SUBTYPES = ["Tout"] + WAKFU_CLASSES

def get_flat_types():
    result = []
    for cat, types in CATEGORIES.items():
        if types:
            for t in types:
                result.append(f"{cat} : {t}")
        else:
            result.append(cat)
    return result

ALL_FLAT_TYPES = get_flat_types()

C = {
    "bg":"#1a1a2e","bg2":"#16213e","surface":"#1e2a45",
    "surface2":"#0f3460","accent":"#e94560","accent2":"#533483",
    "green":"#0cca4a","red":"#e94560","yellow":"#f5d623",
    "orange":"#f5a623","blue":"#4fc3f7","text":"#eee",
    "sub":"#a0a0b8","border":"#333355",
    "step_bg":"#253050","step_fg":"#ddeeff",
}

STEP_TYPES = [
    ("detect",               "🔍 Détecter template"),
    ("attendre_detection",   "🔍 Attendre apparition"),
    ("attendre_disparition", "🔍 Attendre disparition"),
    ("hover",                "🖱 Survoler"),
    ("click_gauche",         "🖱 Clic gauche"),
    ("click_droit",          "🖱 Clic droit"),
    ("detect_then_click",    "🖱 Chercher → clic gauche"),
    ("detect_then_rclick",   "🖱 Chercher → clic droit"),
    ("clic_position",        "🖱 Clic position fixe (x,y)"),
    ("clic_grille",          "🖱 Clic case grille (col,row)"),
    ("touche",               "⌨ Touche unique"),
    ("combo_touches",        "⌨ Combo (ex: ctrl+a)"),
    ("bind_slot",            "⌨ Slot barre (1-9)"),
    ("wait",                 "⏱ Attendre (ms)"),
    ("si_detecte_alors",     "⚡ Si détecté → séquence"),
    ("si_absent_alors",      "⚡ Si absent → séquence"),
    ("sous_sequence",        "⚡ Lancer séquence"),
    ("pause_si_present",     "⚡ Pause si détecté"),
]
STEP_DICT = dict(STEP_TYPES)

def parse_step_type(combo_value):
    for key, label in STEP_TYPES:
        if label in combo_value or combo_value.startswith(key):
            return key
    parts = combo_value.split(" — ")
    return parts[0].strip() if parts else combo_value

KEY_PRESETS = {
    "Barre de sorts (AZERTY)": {
        "1":"&","2":"é","3":'"',"4":"'","5":"(",
        "6":"-","7":"è","8":"_","9":"ç","0":"à",
    },
    "Barre de sorts (QWERTY)": {
        "1":"1","2":"2","3":"3","4":"4","5":"5",
        "6":"6","7":"7","8":"8","9":"9","0":"0",
    },
    "Déplacement": {"Haut":"z","Bas":"s","Gauche":"q","Droite":"d"},
    "Actions": {
        "Passer tour":"F1","Fin de tour":"F2",
        "Inventaire":"i","Carte":"m","Quêtes":"j",
    },
}
SLOT_KEYS = KEY_PRESETS["Barre de sorts (AZERTY)"]

COMMON_KEYS = [
    "── Lettres ──",
    "a","b","c","d","e","f","g","h","i","j","k","l","m",
    "n","o","p","q","r","s","t","u","v","w","x","y","z",
    "── Chiffres ──",
    "0","1","2","3","4","5","6","7","8","9",
    "── Fonctions ──",
    "F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12",
    "── Spéciales ──",
    "space","enter","tab","escape","backspace","delete",
    "up","down","left","right",
    "── AZERTY (sorts) ──",
    "&","é",'"',"'","(","-","è","_","ç","à",
    "── Modifieurs ──",
    "ctrl","alt","shift",
]


# ═══════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════
class WakfuVisionApp:
    def __init__(self):
        self.config = load_config()
        # Restore custom categories from config
        for cat_name, cat_types in self.config.get("custom_categories", {}).items():
            if cat_name not in CATEGORIES:
                CATEGORIES[cat_name] = cat_types
                if cat_name not in CATEGORY_LIST:
                    CATEGORY_LIST.append(cat_name)
            else:
                for t in cat_types:
                    if t not in CATEGORIES[cat_name]:
                        CATEGORIES[cat_name].append(t)

        self.root = tk.Tk()
        self.root.title("Vision Automator v4.0")
        self.root.geometry("1100x820")
        self.root.configure(bg=C["bg"])
        self.root.minsize(900, 650)

        self.selected_hwnd      = None
        self.scanning           = False
        self.paused             = False
        self.scan_thread        = None
        self.last_clipboard_img = None
        self.last_clipboard_cv  = None
        self.template_cache     = {}
        self._sort_reverse      = {}
        self._preview_photo     = None
        self._lib_preview_photo = None
        self._calib_photo       = None
        self._scan_photo        = None
        self._current_suggestion = ""
        self._tpl_name_to_tid   = {}
        self._window_map        = {}
        self._calib_img         = None
        self._calib_points      = []
        self._calib_scale       = 1.0
        self._calib_offset      = (0, 0)
        self._calib_selected_pt = None
        self._calib_dragging    = False
        self._active_seq_idx    = None
        self._scan_frame_count  = 0
        self._scan_det_count    = 0
        self._scan_last_error   = ""
        self._grid_origin_mode  = False

        self._build_styles()
        self._build_ui()
        self._load_library()
        self._setup_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ══════════════════════════════════════════════════════
    # STYLES
    # ══════════════════════════════════════════════════════
    def _build_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=C["bg"], foreground=C["text"], borderwidth=0)
        style.configure("TNotebook", background=C["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=C["surface"], foreground=C["text"],
                        padding=[14,6], font=("Segoe UI",10))
        style.map("TNotebook.Tab",
                  background=[("selected", C["accent"])],
                  foreground=[("selected","#fff")])
        style.configure("TFrame",    background=C["bg"])
        style.configure("TLabel",    background=C["bg"], foreground=C["text"], font=("Segoe UI",10))
        style.configure("TButton",   background=C["surface"], foreground=C["text"],
                        font=("Segoe UI",10), padding=[10,4])
        style.map("TButton", background=[("active", C["surface2"])])
        style.configure("TCombobox", fieldbackground=C["surface2"], background=C["surface2"],
                        foreground=C["text"], selectbackground=C["accent2"], selectforeground="white",
                        arrowcolor=C["text"])
        style.map("TCombobox",
                  fieldbackground=[("readonly",C["surface2"]),("disabled",C["surface"])],
                  foreground=[("readonly",C["text"]),("disabled",C["sub"])],
                  selectbackground=[("readonly",C["accent2"])],
                  selectforeground=[("readonly","white")])
        self.root.option_add("*TCombobox*Listbox.background",       C["surface2"])
        self.root.option_add("*TCombobox*Listbox.foreground",       C["text"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", C["accent2"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", "white")
        self.root.option_add("*TCombobox*Listbox.font",             ("Segoe UI",9))
        style.configure("Treeview", background=C["surface"], foreground=C["text"],
                        fieldbackground=C["surface"], font=("Segoe UI",9))
        style.configure("Treeview.Heading", background=C["surface2"], foreground=C["text"],
                        font=("Segoe UI",9,"bold"))
        style.map("Treeview", background=[("selected",C["accent2"])])

    # ══════════════════════════════════════════════════════
    # UI
    # ══════════════════════════════════════════════════════
    def _build_ui(self):
        hdr = tk.Frame(self.root, bg=C["bg"], pady=4)
        hdr.pack(fill="x", padx=10)
        tk.Label(hdr, text="VISION AUTOMATOR v4.0", bg=C["bg"], fg=C["accent"],
                 font=("Segoe UI",15,"bold")).pack(side="left")
        self.pause_lbl = tk.Label(hdr, text="", bg=C["bg"], fg=C["yellow"],
                                  font=("Segoe UI",10,"bold"))
        self.pause_lbl.pack(side="left", padx=20)
        self.status_lbl = tk.Label(hdr, text="Aucun processus", bg=C["bg"],
                                   fg=C["sub"], font=("Segoe UI",9))
        self.status_lbl.pack(side="right")

        pf = tk.Frame(self.root, bg=C["surface"], pady=5, padx=8)
        pf.pack(fill="x", padx=10, pady=(0,4))
        tk.Label(pf, text="Fenêtre:", bg=C["surface"], fg=C["text"],
                 font=("Segoe UI",10)).pack(side="left")
        self.proc_var   = tk.StringVar()
        self.proc_combo = ttk.Combobox(pf, textvariable=self.proc_var,
                                       state="readonly", width=60)
        self.proc_combo.pack(side="left", padx=(6,4))
        self.proc_combo.bind("<<ComboboxSelected>>", self._on_proc_selected)
        tk.Button(pf, text="↻", bg=C["surface2"], fg=C["text"], relief="flat",
                  font=("Segoe UI",11), cursor="hand2", width=3,
                  command=self._refresh_procs).pack(side="left", padx=2)
        tk.Label(pf, text="F5=Coller  F8=Scan  F9=Pause  F10=Quitter",
                 bg=C["surface"], fg=C["sub"], font=("Segoe UI",8)).pack(side="right")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=4)

        self.tab_capture     = tk.Frame(self.notebook, bg=C["bg"])
        self.tab_library     = tk.Frame(self.notebook, bg=C["bg"])
        self.tab_sequences   = tk.Frame(self.notebook, bg=C["bg"])
        self.tab_scan        = tk.Frame(self.notebook, bg=C["bg"])
        self.tab_calibration = tk.Frame(self.notebook, bg=C["bg"])

        self.notebook.add(self.tab_capture,     text="  📷 Capture  ")
        self.notebook.add(self.tab_library,     text="  📚 Bibliothèque  ")
        self.notebook.add(self.tab_scan,        text="  🔍 Scan  ")
        self.notebook.add(self.tab_sequences,   text="  ⚡ Séquences  ")
        self.notebook.add(self.tab_calibration, text="  🎯 Calibration  ")

        self._build_capture_tab()
        self._build_library_tab()
        self._build_sequences_tab()
        self._build_scan_tab()
        self._build_calibration_tab()

        # ── Log bar ──
        lf = tk.Frame(self.root, bg=C["bg2"], height=100)
        lf.pack(fill="x", side="bottom", padx=10, pady=(0,6))
        lf.pack_propagate(False)
        lh = tk.Frame(lf, bg=C["bg2"])
        lh.pack(fill="x")
        tk.Label(lh, text="Log", bg=C["bg2"], fg=C["sub"],
                 font=("Segoe UI",9,"bold")).pack(side="left", padx=6, pady=2)
        tk.Button(lh, text="📋 Copier log", bg=C["surface"], fg=C["text"],
                  relief="flat", font=("Segoe UI",8), cursor="hand2",
                  command=self._copy_log).pack(side="right", padx=2, pady=2)
        tk.Button(lh, text="Clear", bg=C["surface"], fg=C["text"],
                  relief="flat", font=("Segoe UI",8), cursor="hand2",
                  command=self._clear_log).pack(side="right", padx=6, pady=2)
        self.log_text = tk.Text(lf, bg=C["bg2"], fg=C["sub"],
                                font=("Consolas",9), wrap="word",
                                borderwidth=0, highlightthickness=0,
                                state="disabled", height=5)
        sb = tk.Scrollbar(lf, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True, padx=4, pady=2)
        self.log_text.tag_configure("info",  foreground=C["sub"])
        self.log_text.tag_configure("ok",    foreground=C["green"])
        self.log_text.tag_configure("warn",  foreground=C["yellow"])
        self.log_text.tag_configure("error", foreground=C["red"])

        self._refresh_procs()
        self._log("Vision Automator v4.0 — prêt.", "ok")

    # ══════════════════════════════════════════════════════
    # CAPTURE TAB
    # ══════════════════════════════════════════════════════
    def _build_capture_tab(self):
        parent = self.tab_capture
        main = tk.Frame(parent, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=16, pady=12)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)

        # Gauche : aperçu
        left = tk.Frame(main, bg=C["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0,12))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        hint_frame = tk.Frame(left, bg=C["surface"], highlightbackground=C["border"],
                              highlightthickness=1)
        hint_frame.grid(row=0, column=0, sticky="ew", pady=(0,8))
        tk.Label(hint_frame,
                 text="  ✂  Win+Shift+S  →  capturer une zone,  puis  F5  pour coller",
                 bg=C["surface"], fg=C["accent"],
                 font=("Segoe UI Semibold",9), pady=8).pack(fill="x")

        preview_border = tk.Frame(left, bg=C["border"],
                                  highlightbackground=C["accent"], highlightthickness=2)
        preview_border.grid(row=1, column=0, sticky="nsew")
        preview_border.rowconfigure(0, weight=1)
        preview_border.columnconfigure(0, weight=1)
        preview_inner = tk.Frame(preview_border, bg=C["surface"])
        preview_inner.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        preview_inner.rowconfigure(0, weight=1)
        preview_inner.columnconfigure(0, weight=1)
        self.preview_lbl = tk.Label(preview_inner, text="📷\n\nAperçu de la capture",
                                    bg=C["surface"], fg=C["sub"],
                                    font=("Segoe UI",11), justify="center")
        self.preview_lbl.grid(row=0, column=0, sticky="nsew")

        tk.Button(left, text="📋  Coller (F5)", bg=C["accent"], fg="white",
                  font=("Segoe UI",11,"bold"), relief="flat", cursor="hand2",
                  padx=20, pady=8,
                  command=self._grab_clipboard).grid(row=2, column=0, pady=(10,0))

        # Droite : formulaire
        right = tk.Frame(main, bg=C["surface"], highlightbackground=C["border"],
                         highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")

        header = tk.Frame(right, bg=C["accent"], height=38)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="💾  Enregistrer le template",
                 font=("Segoe UI Semibold",10), bg=C["accent"], fg="white").pack(side="left", padx=12)

        form = tk.Frame(right, bg=C["surface"])
        form.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(form, text="NOM", bg=C["surface"], fg=C["sub"],
                 font=("Segoe UI Semibold",8), anchor="w").pack(fill="x", pady=(0,2))
        self.name_var   = tk.StringVar()
        self.name_entry = tk.Entry(form, textvariable=self.name_var,
                                   bg=C["surface2"], fg=C["text"],
                                   font=("Segoe UI",11), relief="flat",
                                   insertbackground=C["text"], bd=0)
        self.name_entry.pack(fill="x", ipady=6)
        self.name_entry.bind("<Tab>",        self._accept_suggestion)
        self.name_entry.bind("<KeyRelease>", self._on_name_typing)
        self.suggestion_lbl = tk.Label(form, text="", bg=C["surface"], fg=C["sub"],
                                       font=("Segoe UI",8,"italic"), anchor="w")
        self.suggestion_lbl.pack(fill="x", pady=(2,8))

        tk.Label(form, text="DOSSIER", bg=C["surface"], fg=C["sub"],
                 font=("Segoe UI Semibold",8), anchor="w").pack(fill="x", pady=(0,2))
        self.cat_var   = tk.StringVar()
        self.cat_combo = ttk.Combobox(form, textvariable=self.cat_var, font=("Segoe UI",10), values=self.config.get("categories",[]))
        folder_row = tk.Frame(form, bg=C["bg"])
        folder_row.pack(fill="x")
        self.cat_combo.pack(side="left", fill="x", expand=True, ipady=4, in_=folder_row)
        tk.Button(folder_row, text="+", bg=C["accent"], fg="white",
                  font=("Segoe UI",9,"bold"), width=3, relief="flat", cursor="hand2",
                  command=self._add_dynamic_folder).pack(side="right", padx=(4,0), ipady=3)

        tk.Frame(form, bg=C["surface"], height=10).pack(fill="x")

        tk.Label(form, text="CATÉGORIE", bg=C["surface"], fg=C["sub"],
                 font=("Segoe UI Semibold",8), anchor="w").pack(fill="x", pady=(0,2))
        self.tpl_cat_var   = tk.StringVar(value="Ressource")
        self.tpl_cat_combo = ttk.Combobox(form, textvariable=self.tpl_cat_var,
                                           state="readonly", font=("Segoe UI",10),
                                           values=CATEGORY_LIST)
        cat_row = tk.Frame(form, bg=C["bg"])
        cat_row.pack(fill="x")
        self.tpl_cat_combo.pack(side="left", fill="x", expand=True, ipady=4, in_=cat_row)
        tk.Button(cat_row, text="+", bg=C["accent"], fg="white",
                  font=("Segoe UI",9,"bold"), width=3, relief="flat", cursor="hand2",
                  command=self._add_dynamic_category).pack(side="right", padx=(4,0), ipady=3)
        self.tpl_cat_combo.bind("<<ComboboxSelected>>", self._on_tpl_cat_changed)

        tk.Frame(form, bg=C["surface"], height=10).pack(fill="x")

        tk.Label(form, text="TYPE", bg=C["surface"], fg=C["sub"],
                 font=("Segoe UI Semibold",8), anchor="w").pack(fill="x", pady=(0,2))
        self.type_var   = tk.StringVar()
        self.type_combo = ttk.Combobox(form, textvariable=self.type_var,
                                        state="readonly", font=("Segoe UI",10), values=[])
        type_row = tk.Frame(form, bg=C["bg"])
        type_row.pack(fill="x")
        self.type_combo.pack(side="left", fill="x", expand=True, ipady=4, in_=type_row)
        tk.Button(type_row, text="+", bg=C["accent"], fg="white",
                  font=("Segoe UI",9,"bold"), width=3, relief="flat", cursor="hand2",
                  command=self._add_dynamic_type).pack(side="right", padx=(4,0), ipady=3)
        self._on_tpl_cat_changed()

        tk.Frame(form, bg=C["surface"], height=10).pack(fill="x")
        self.auto_lbl = tk.Label(form, text="", bg=C["surface"], fg=C["green"],
                                 font=("Segoe UI",9,"italic"), anchor="w")
        self.auto_lbl.pack(fill="x", pady=(4,12))
        tk.Frame(form, bg=C["border"], height=1).pack(fill="x", pady=(0,12))

        btn_frame = tk.Frame(form, bg=C["surface"])
        btn_frame.pack(fill="x")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        tk.Button(btn_frame, text="💾 Nouveau template", bg=C["green"], fg="white",
                  font=("Segoe UI",10,"bold"), relief="flat", cursor="hand2", pady=8,
                  command=self._save_template).grid(row=0, column=0, sticky="ew", padx=(0,4))
        tk.Button(btn_frame, text="➕ Ajouter variante", bg=C["orange"], fg="white",
                  font=("Segoe UI",10,"bold"), relief="flat", cursor="hand2", pady=8,
                  command=self._add_variant).grid(row=0, column=1, sticky="ew", padx=(4,0))
        self.root.bind("<Control-s>", lambda e: self._save_template())

    def _on_tpl_cat_changed(self, event=None):
        cat   = self.tpl_cat_var.get()
        types = CATEGORIES.get(cat, [])
        self.type_combo["values"] = types
        if types:
            self.type_var.set(types[0])
        else:
            self.type_var.set("(aucun)")

    def _add_dynamic_category(self):
        name = simpledialog.askstring("Nouvelle catégorie", "Nom :", parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()
        if name in CATEGORIES:
            self._log(f"Catégorie '{name}' existe déjà", "error"); return
        CATEGORIES[name] = []
        CATEGORY_LIST.append(name)
        if "custom_categories" not in self.config:
            self.config["custom_categories"] = {}
        self.config["custom_categories"][name] = []
        save_config(self.config)
        self.tpl_cat_combo["values"] = CATEGORY_LIST
        self.tpl_cat_var.set(name)
        self._on_tpl_cat_changed()
        self._log(f"Catégorie ajoutée : {name}", "ok")

    def _add_dynamic_type(self):
        cat = self.tpl_cat_var.get()
        if not cat:
            self._log("Sélectionne d'abord une catégorie", "error"); return
        name = simpledialog.askstring("Nouveau type", f"Type pour '{cat}' :", parent=self.root)
        if not name or not name.strip():
            return
        name  = name.strip()
        types = CATEGORIES.get(cat, [])
        if name in types:
            self._log(f"Type '{name}' existe déjà", "error"); return
        types.append(name)
        CATEGORIES[cat] = types
        if "custom_categories" not in self.config:
            self.config["custom_categories"] = {}
        self.config["custom_categories"][cat] = types
        save_config(self.config)
        self.type_combo["values"] = types
        self.type_var.set(name)
        self._log(f"Type ajouté : {cat} > {name}", "ok")

    def _add_dynamic_folder(self):
        name = simpledialog.askstring("Nouveau dossier", "Nom :", parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()
        current = list(self.cat_combo["values"]) if self.cat_combo["values"] else []
        if name not in current:
            current.append(name)
            self.cat_combo["values"] = current
        self.cat_var.set(name)
        self._log(f"Dossier ajouté : {name}", "ok")

    # ══════════════════════════════════════════════════════
    # LIBRARY TAB
    # ══════════════════════════════════════════════════════
    def _build_library_tab(self):
        parent = self.tab_library
        tb = tk.Frame(parent, bg=C["bg"])
        tb.pack(fill="x", padx=4, pady=(6,2))
        for txt, cmd, bg_c in [
            ("+ Catégorie",  self._add_category,         C["accent2"]),
            ("Renommer",     self._rename_selected,       C["surface2"]),
            ("Chg catégorie",self._move_selected,         C["surface2"]),
            ("Chg type",     self._change_type_selected,  C["surface2"]),
            ("Supprimer",    self._delete_selected,       C["red"]),
        ]:
            fg_c = "white" if bg_c != C["surface2"] else C["text"]
            tk.Button(tb, text=txt, bg=bg_c, fg=fg_c, relief="flat",
                      cursor="hand2", font=("Segoe UI",9), command=cmd).pack(side="left", padx=2)
        tk.Button(tb, text="📂 Dossier", bg=C["surface2"], fg=C["text"],
                  relief="flat", cursor="hand2", font=("Segoe UI",9),
                  command=lambda: os.startfile(LIBRARY_DIR)).pack(side="right", padx=2)

        ff = tk.Frame(parent, bg=C["bg"])
        ff.pack(fill="x", padx=4, pady=2)
        tk.Label(ff, text="Filtre:", bg=C["bg"], fg=C["sub"]).pack(side="left")
        self.filter_var   = tk.StringVar(value="Tout")
        self.filter_combo = ttk.Combobox(ff, textvariable=self.filter_var,
                                          state="readonly", width=20,
                                          values=["Tout"] + ALL_FLAT_TYPES)
        self.filter_combo.pack(side="left", padx=4)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_library_view())

        cols = ("name","type","category","variants","size")
        self.lib_tree = ttk.Treeview(parent, columns=cols, show="headings", height=14)
        for col, label, w in [("name","Nom",180),("type","Type",80),
                               ("category","Catégorie",120),("variants","Variantes",70),
                               ("size","Taille",70)]:
            self.lib_tree.heading(col, text=label, command=lambda c=col: self._sort_tree(c))
            self.lib_tree.column(col, width=w)
        self.lib_tree.pack(fill="both", expand=True, padx=4, pady=4)
        self.lib_tree.bind("<<TreeviewSelect>>", self._on_lib_select)

        bp = tk.Frame(parent, bg=C["surface"], height=70)
        bp.pack(fill="x", padx=4, pady=(0,4))
        self.lib_preview_frame = tk.Frame(bp, bg=C["surface"])
        self.lib_preview_frame.pack(side="left", padx=8, pady=4)
        self.lib_preview_lbl = tk.Label(self.lib_preview_frame, bg=C["surface"])
        self.lib_preview_lbl.pack(side="left")
        self._lib_variant_photos = []
        self.lib_info_lbl = tk.Label(bp, bg=C["surface"], fg=C["text"],
                                     font=("Segoe UI",9), justify="left")
        self.lib_info_lbl.pack(side="left", padx=8, pady=4)

    # ══════════════════════════════════════════════════════
    # SEQUENCES TAB
    # ══════════════════════════════════════════════════════
    def _build_sequences_tab(self):
        parent = self.tab_sequences
        main   = tk.Frame(parent, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=4, pady=4)

        left = tk.Frame(main, bg=C["surface"], width=280)
        left.pack(side="left", fill="y", padx=(0,4))
        left.pack_propagate(False)

        tk.Label(left, text="Séquences (priorité = ordre)", bg=C["surface"],
                 fg=C["text"], font=("Segoe UI",10,"bold")).pack(pady=4)
        self.seq_tree = ttk.Treeview(left, show="tree", height=18, selectmode="browse")
        self.seq_tree.pack(fill="both", expand=True, padx=4, pady=2)
        self.seq_tree.bind("<<TreeviewSelect>>", self._on_seq_tree_select)
        self.seq_tree.tag_configure("disabled", foreground=C["sub"])
        self.seq_tree.tag_configure("enabled",  foreground=C["green"])

        sb = tk.Frame(left, bg=C["surface"])
        sb.pack(fill="x", padx=4, pady=4)
        for txt, cmd, bg_c in [
            ("+",        self._add_sequence,       C["green"]),
            ("+ Enfant", self._add_child_sequence, C["accent2"]),
            ("✎",        self._rename_sequence,    C["surface2"]),
            ("⬆",        self._move_seq_up,        C["surface2"]),
            ("⬇",        self._move_seq_down,      C["surface2"]),
            ("📋",       self._copy_sequence,       C["surface2"]),
            ("✕",        self._delete_sequence,    C["red"]),
        ]:
            fg_c = "white" if bg_c not in (C["surface2"],) else C["text"]
            tk.Button(sb, text=txt, bg=bg_c, fg=fg_c, relief="flat",
                      font=("Segoe UI",9,"bold"), width=3,
                      cursor="hand2", command=cmd).pack(side="left", padx=1)

        enf = tk.Frame(left, bg=C["surface"])
        enf.pack(fill="x", padx=4, pady=2)
        self.seq_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(enf, text="Séquence active", variable=self.seq_enabled_var,
                       bg=C["surface"], fg=C["text"], selectcolor=C["surface2"],
                       font=("Segoe UI",9), command=self._toggle_seq_enabled).pack(side="left")

        right = tk.Frame(main, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)

        self.seq_name_lbl = tk.Label(right, text="← Sélectionne une séquence",
                                     bg=C["bg"], fg=C["accent"],
                                     font=("Segoe UI",11,"bold"))
        self.seq_name_lbl.pack(pady=(4,2), anchor="w", padx=6)

        # Conditions
        cond_frame = tk.LabelFrame(right, text=" Conditions (la séquence ne se lance que si…) ",
                                   bg=C["bg"], fg=C["yellow"], font=("Segoe UI",9,"bold"))
        cond_frame.pack(fill="x", padx=4, pady=(2,4))
        self.cond_listbox = tk.Listbox(cond_frame, bg=C["step_bg"], fg=C["step_fg"],
                                       font=("Consolas",9), relief="flat",
                                       selectbackground=C["accent2"],
                                       selectforeground="white", height=3)
        self.cond_listbox.pack(fill="x", padx=4, pady=2)
        cond_builder = tk.Frame(cond_frame, bg=C["bg"])
        cond_builder.pack(fill="x", padx=4, pady=2)
        tk.Label(cond_builder, text="Si", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI",9)).pack(side="left")
        self.cond_template_var   = tk.StringVar()
        self.cond_template_combo = ttk.Combobox(cond_builder,
                                                textvariable=self.cond_template_var,
                                                state="readonly", width=30)
        self.cond_template_combo.pack(side="left", padx=4)
        self.cond_mode_var   = tk.StringVar(value="absent")
        self.cond_mode_combo = ttk.Combobox(cond_builder, textvariable=self.cond_mode_var,
                                             state="readonly", width=12,
                                             values=["est absent ✗","est présent ✓"])
        self.cond_mode_combo.current(0)
        self.cond_mode_combo.pack(side="left", padx=4)
        tk.Button(cond_builder, text="+ Condition", bg=C["green"], fg="white",
                  relief="flat", font=("Segoe UI",8,"bold"), cursor="hand2",
                  command=self._add_condition).pack(side="left", padx=4)
        tk.Button(cond_builder, text="✕", bg=C["red"], fg="white",
                  relief="flat", font=("Segoe UI",8,"bold"), cursor="hand2",
                  width=2, command=self._delete_condition).pack(side="left", padx=2)

        # Steps
        self.steps_listbox = tk.Listbox(right, bg=C["step_bg"], fg=C["step_fg"],
                                         font=("Consolas",10), relief="flat",
                                         selectbackground=C["accent2"],
                                         selectforeground="white", height=10)
        self.steps_listbox.pack(fill="both", expand=True, padx=4, pady=2)

        builder = tk.LabelFrame(right, text=" Ajouter une étape ", bg=C["bg"],
                                fg=C["accent"], font=("Segoe UI",9,"bold"))
        builder.pack(fill="x", padx=4, pady=4)

        r1 = tk.Frame(builder, bg=C["bg"])
        r1.pack(fill="x", padx=6, pady=2)
        tk.Label(r1, text="Action:", bg=C["bg"], fg=C["blue"],
                 font=("Segoe UI",9,"bold")).pack(side="left")
        self.step_type_var   = tk.StringVar()
        self.step_type_combo = ttk.Combobox(r1, textvariable=self.step_type_var,
                                             state="readonly", width=32)
        self.step_type_combo["values"] = [v for _,v in STEP_TYPES]
        self.step_type_combo.current(0)
        self.step_type_combo.pack(side="left", padx=6)
        self.step_type_combo.bind("<<ComboboxSelected>>", self._on_step_type_changed)

        r2 = tk.Frame(builder, bg=C["bg"])
        r2.pack(fill="x", padx=6, pady=2)
        tk.Label(r2, text="Template:", bg=C["bg"], fg=C["blue"],
                 font=("Segoe UI",9,"bold")).pack(side="left")
        self.step_template_var   = tk.StringVar()
        self.step_template_combo = ttk.Combobox(r2, textvariable=self.step_template_var,
                                                 state="readonly", width=38)
        self.step_template_combo.pack(side="left", padx=6)

        self.step_subseq_frame = tk.Frame(builder, bg=C["bg"])
        self.step_subseq_frame.pack(fill="x", padx=6, pady=2)
        tk.Label(self.step_subseq_frame, text="Sous-séq:", bg=C["bg"], fg=C["blue"],
                 font=("Segoe UI",9,"bold")).pack(side="left")
        self.step_subseq_var   = tk.StringVar()
        self.step_subseq_combo = ttk.Combobox(self.step_subseq_frame,
                                               textvariable=self.step_subseq_var,
                                               state="readonly", width=35)
        self.step_subseq_combo.pack(side="left", padx=6)
        self.step_subseq_frame.pack_forget()

        r3 = tk.Frame(builder, bg=C["bg"])
        r3.pack(fill="x", padx=6, pady=2)
        tk.Label(r3, text="Valeur:", bg=C["bg"], fg=C["blue"],
                 font=("Segoe UI",9)).pack(side="left")
        self.step_value_var   = tk.StringVar(value="300")
        self.step_value_entry = tk.Entry(r3, textvariable=self.step_value_var,
                                          bg=C["surface2"], fg=C["text"],
                                          font=("Segoe UI",9), relief="flat", width=12,
                                          insertbackground=C["text"])
        self.step_value_entry.pack(side="left", padx=4)
        self.key_picker_var = tk.StringVar()
        self.key_picker     = ttk.Combobox(r3, textvariable=self.key_picker_var,
                                            state="readonly", width=14)
        self.key_picker["values"] = COMMON_KEYS
        self.key_picker.pack(side="left", padx=2)
        self.key_picker.bind("<<ComboboxSelected>>", self._on_key_picked)
        self.capture_key_btn = tk.Button(r3, text="🎹 Capturer",
                                          bg=C["surface2"], fg=C["text"],
                                          relief="flat", font=("Segoe UI",8),
                                          cursor="hand2", command=self._capture_key_press)
        self.capture_key_btn.pack(side="left", padx=2)
        self.step_value_hint = tk.Label(r3, text="", bg=C["bg"],
                                         fg=C["sub"], font=("Segoe UI",8))
        self.step_value_hint.pack(side="left", padx=4)

        btns = tk.Frame(builder, bg=C["bg"])
        btns.pack(fill="x", padx=6, pady=4)
        for txt, cmd, bg_c in [
            ("+ Ajouter",  self._add_step,     C["green"]),
            ("✎ Modifier", self._edit_step,    C["orange"]),
            ("⬆",          self._move_step_up, C["surface2"]),
            ("⬇",          self._move_step_down,C["surface2"]),
            ("📋 Copier",  self._copy_step,    C["surface2"]),
            ("✕ Suppr",    self._delete_step,  C["red"]),
        ]:
            fg_c = "white" if bg_c not in (C["surface2"],) else C["text"]
            tk.Button(btns, text=txt, bg=bg_c, fg=fg_c, relief="flat",
                      font=("Segoe UI",9), cursor="hand2",
                      command=cmd).pack(side="left", padx=2)

    # ══════════════════════════════════════════════════════
    # SCAN TAB
    # ══════════════════════════════════════════════════════
    def _build_scan_tab(self):
        parent = self.tab_scan
        top = tk.Frame(parent, bg=C["bg"])
        top.pack(fill="x", padx=8, pady=6)

        self.scan_btn = tk.Button(top, text="▶ Démarrer la séquence (F8)",
                                  bg=C["green"], fg="white",
                                  font=("Segoe UI",11,"bold"),
                                  relief="flat", cursor="hand2", padx=16, pady=6,
                                  command=self._toggle_scan)
        self.scan_btn.pack(side="left")
        self.scan_stats_lbl = tk.Label(top, text="", bg=C["bg"], fg=C["sub"],
                                       font=("Segoe UI",9))
        self.scan_stats_lbl.pack(side="left", padx=16)

        ctrl = tk.Frame(top, bg=C["bg"])
        ctrl.pack(side="right")
        tk.Label(ctrl, text="Seuil:", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI",9)).pack(side="left")
        self.thresh_var   = tk.DoubleVar(value=self.config["confidence_threshold"])
        self.thresh_scale = tk.Scale(ctrl, from_=0.3, to=1.0, resolution=0.05,
                                     orient="horizontal", variable=self.thresh_var,
                                     bg=C["bg"], fg=C["text"], troughcolor=C["surface2"],
                                     highlightthickness=0, font=("Segoe UI",8),
                                     length=150, showvalue=True,
                                     command=self._on_thresh_changed)
        self.thresh_scale.pack(side="left", padx=4)
        tk.Label(ctrl, text="ms:", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI",9)).pack(side="left", padx=(12,0))
        self.interval_var = tk.IntVar(value=self.config["scan_interval_ms"])
        tk.Entry(ctrl, textvariable=self.interval_var, bg=C["surface2"],
                 fg=C["text"], relief="flat", width=6, font=("Segoe UI",9),
                 insertbackground=C["text"]).pack(side="left", padx=4)

        self.scan_canvas = tk.Canvas(parent, bg="#111", highlightthickness=0)
        self.scan_canvas.pack(fill="both", expand=True, padx=8, pady=(4,2))

        self.scan_det_text = tk.Text(parent, height=5, bg=C["surface"], fg=C["green"],
                                     font=("Consolas",9), relief="flat", state="disabled")
        self.scan_det_text.pack(fill="x", padx=8, pady=(2,8))
        self.scan_det_text.tag_configure("high",   foreground=C["green"])
        self.scan_det_text.tag_configure("medium", foreground=C["yellow"])
        self.scan_det_text.tag_configure("low",    foreground=C["orange"])

    # ══════════════════════════════════════════════════════
    # CALIBRATION TAB
    # ══════════════════════════════════════════════════════
    def _build_calibration_tab(self):
        parent = self.tab_calibration
        parent.configure(bg=C["bg"])

        calib_nb = ttk.Notebook(parent)
        calib_nb.pack(fill="both", expand=True, padx=6, pady=6)
        self._calib_mouse_tab = tk.Frame(calib_nb, bg=C["bg"])
        self._calib_grid_tab  = tk.Frame(calib_nb, bg=C["bg"])
        calib_nb.add(self._calib_mouse_tab, text="  🖱 Calibration souris  ")
        calib_nb.add(self._calib_grid_tab,  text="  🗺 Grille de combat  ")
        self._build_calib_mouse_subtab()
        self._build_calib_grid_subtab()

    def _build_calib_mouse_subtab(self):
        parent = self._calib_mouse_tab
        top = tk.Frame(parent, bg=C["bg"])
        top.pack(fill="x", padx=8, pady=6)

        left_info = tk.Frame(top, bg=C["bg"])
        left_info.pack(side="left", fill="y")
        tk.Label(left_info, text="Calibration souris", bg=C["bg"], fg=C["accent"],
                 font=("Segoe UI",12,"bold")).pack(anchor="w")
        tk.Label(left_info,
                 text=("1. Capture la fenêtre\n"
                       "2. Clique pour poser un point (max 5)\n"
                       "3. Glisse pour déplacer\n"
                       "4. Double-clic → souris va sur le jeu\n"
                       "5. Clic-droit → supprimer un point\n"
                       "6. Ajuste offsets si décalé"),
                 bg=C["bg"], fg=C["sub"], font=("Segoe UI",9),
                 justify="left").pack(anchor="w", pady=4)

        right_btns = tk.Frame(top, bg=C["bg"])
        right_btns.pack(side="right")
        for txt, cmd, bg_c in [
            ("📸 Capturer",    self._calib_capture,  C["accent"]),
            ("🗑 Effacer",     self._calib_clear,    C["surface2"]),
            ("🎯 Tester tous", self._calib_test_all, C["orange"]),
            ("✅ Valider",     self._calib_save,     C["green"]),
        ]:
            fg_c = "white" if bg_c != C["surface2"] else C["text"]
            tk.Button(right_btns, text=txt, bg=bg_c, fg=fg_c,
                      font=("Segoe UI",10,"bold"), relief="flat", cursor="hand2",
                      command=cmd).pack(pady=2, fill="x")

        of = tk.Frame(right_btns, bg=C["bg"])
        of.pack(pady=4)
        tk.Label(of, text="Offset X:", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI",9)).pack(side="left")
        self.offset_x_var = tk.IntVar(value=self.config.get("calibration_offset_x",0))
        tk.Spinbox(of, from_=-50, to=50, textvariable=self.offset_x_var,
                   width=5, font=("Segoe UI",9),
                   command=self._save_offsets).pack(side="left", padx=2)
        tk.Label(of, text="Y:", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI",9)).pack(side="left", padx=(8,0))
        self.offset_y_var = tk.IntVar(value=self.config.get("calibration_offset_y",0))
        tk.Spinbox(of, from_=-50, to=50, textvariable=self.offset_y_var,
                   width=5, font=("Segoe UI",9),
                   command=self._save_offsets).pack(side="left", padx=2)
        tk.Button(of, text="0", bg=C["surface2"], fg=C["text"], relief="flat",
                  font=("Segoe UI",8), width=2,
                  command=self._reset_offsets).pack(side="left", padx=4)

        self.calib_canvas = tk.Canvas(parent, bg=C["bg2"], highlightthickness=0, cursor="crosshair")
        self.calib_canvas.pack(fill="both", expand=True, padx=8, pady=(4,8))
        self.calib_canvas.bind("<Button-1>",         self._calib_click)
        self.calib_canvas.bind("<B1-Motion>",        self._calib_drag)
        self.calib_canvas.bind("<ButtonRelease-1>",  self._calib_release)
        self.calib_canvas.bind("<Double-Button-1>",  self._calib_double_click)
        self.calib_canvas.bind("<Configure>",        self._calib_redraw)
        self.calib_canvas.bind("<Button-3>",         self._calib_delete_point)

        self.calib_info_lbl = tk.Label(parent, text="", bg=C["bg"], fg=C["green"],
                                       font=("Segoe UI",9))
        self.calib_info_lbl.pack(pady=(0,4))
        self._calib_points = [
            (p["img_x"], p["img_y"])
            for p in self.config.get("calibration_points", [])
        ]

    def _build_calib_grid_subtab(self):
        parent = self._calib_grid_tab

        # Variables grille
        self.grid_cw_var      = tk.IntVar(value=self.config.get("grid",{}).get("cell_w",43))
        self.grid_ch_var      = tk.IntVar(value=self.config.get("grid",{}).get("cell_h",22))
        self.grid_ox_var      = tk.IntVar(value=self.config.get("grid",{}).get("origin_x",0))
        self.grid_oy_var      = tk.IntVar(value=self.config.get("grid",{}).get("origin_y",0))
        self.grid_cols_var    = tk.IntVar(value=self.config.get("grid",{}).get("cols",20))
        self.grid_rows_var    = tk.IntVar(value=self.config.get("grid",{}).get("rows",20))
        self.grid_visible_var = tk.BooleanVar(value=self.config.get("grid",{}).get("visible",False))

        pw = tk.PanedWindow(parent, orient=tk.HORIZONTAL, bg=C["bg"], sashwidth=4, bd=0)
        pw.pack(fill="both", expand=True, padx=6, pady=6)

        # Gauche : canvas
        left = tk.Frame(pw, bg=C["bg"])
        pw.add(left, width=600, minsize=400)

        lh = tk.Frame(left, bg=C["accent"], height=34)
        lh.pack(fill="x")
        lh.pack_propagate(False)
        tk.Label(lh, text="🗺  Visualisation de la grille",
                 font=("Segoe UI Semibold",10), bg=C["accent"], fg="white").pack(side="left", padx=10)

        self.grid_canvas = tk.Canvas(left, bg="#0a0a1a", highlightthickness=0, cursor="crosshair")
        self.grid_canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self.grid_canvas.bind("<Button-1>", self._grid_canvas_click)
        self.grid_canvas.bind("<Motion>",   self._grid_canvas_motion)
        self.grid_canvas.bind("<Configure>",self._grid_canvas_redraw)

        self.grid_info_lbl = tk.Label(left, text="Survolez pour voir les coordonnées",
                                      bg=C["bg"], fg=C["sub"], font=("Segoe UI",9))
        self.grid_info_lbl.pack(pady=(0,4))

        grid_bar = tk.Frame(left, bg=C["bg"])
        grid_bar.pack(fill="x", padx=4, pady=(0,4))
        tk.Button(grid_bar, text="📸 Capturer", bg=C["accent"], fg="white",
                  font=("Segoe UI",10,"bold"), relief="flat", cursor="hand2",
                  command=self._grid_capture).pack(side="left", padx=2)
        self.grid_show_detect_var  = tk.BooleanVar(value=True)
        self.grid_show_overlay_var = tk.BooleanVar(value=True)
        tk.Checkbutton(grid_bar, text="Détections",
                       variable=self.grid_show_detect_var, bg=C["bg"], fg=C["text"],
                       selectcolor=C["surface2"], font=("Segoe UI",9),
                       command=self._grid_canvas_redraw).pack(side="left", padx=4)
        tk.Checkbutton(grid_bar, text="Grille",
                       variable=self.grid_show_overlay_var, bg=C["bg"], fg=C["text"],
                       selectcolor=C["surface2"], font=("Segoe UI",9),
                       command=self._grid_canvas_redraw).pack(side="left", padx=4)

        # Droite : params
        right = tk.Frame(pw, bg=C["surface"])
        pw.add(right, width=280, minsize=220)

        rh = tk.Frame(right, bg=C["accent2"], height=34)
        rh.pack(fill="x")
        rh.pack_propagate(False)
        tk.Label(rh, text="⚙  Paramètres grille",
                 font=("Segoe UI Semibold",10), bg=C["accent2"], fg="white").pack(side="left", padx=10)

        cf = tk.Frame(right, bg=C["surface"])
        cf.pack(fill="both", expand=True, padx=8, pady=8)

        s4 = tk.LabelFrame(cf, text="  Affichage  ", bg=C["surface"], fg=C["accent"],
                            font=("Segoe UI Semibold",9), bd=1, relief="groove")
        s4.pack(fill="x", pady=(0,8))
        tk.Checkbutton(s4, text="Afficher la grille sur l'onglet Scan",
                       variable=self.grid_visible_var, bg=C["surface"], fg=C["text"],
                       selectcolor=C["surface2"], font=("Segoe UI",9),
                       command=self._save_grid).pack(anchor="w", padx=8, pady=4)

        s5 = tk.LabelFrame(cf, text="  Paramètres cellule  ", bg=C["surface"], fg=C["accent"],
                            font=("Segoe UI Semibold",9), bd=1, relief="groove")
        s5.pack(fill="x", pady=(0,8))
        for label, var in [("Largeur cellule:", self.grid_cw_var),
                            ("Hauteur cellule:", self.grid_ch_var),
                            ("Origine X:",       self.grid_ox_var),
                            ("Origine Y:",       self.grid_oy_var),
                            ("Colonnes:",        self.grid_cols_var),
                            ("Lignes:",          self.grid_rows_var)]:
            row = tk.Frame(s5, bg=C["surface"])
            row.pack(fill="x", padx=8, pady=2)
            tk.Label(row, text=label, bg=C["surface"], fg=C["text"],
                     font=("Segoe UI",9), width=16, anchor="w").pack(side="left")
            tk.Spinbox(row, from_=0, to=9999, textvariable=var, width=6,
                       font=("Segoe UI",9),
                       command=self._on_grid_param_change).pack(side="left", padx=4)

        tk.Button(cf, text="💾 Sauvegarder grille", bg=C["green"], fg="white",
                  font=("Segoe UI",10,"bold"), relief="flat", cursor="hand2",
                  command=self._save_grid).pack(fill="x", pady=4)

    # ══════════════════════════════════════════════════════
    # PROCESS
    # ══════════════════════════════════════════════════════
    def _refresh_procs(self):
        self._window_map.clear()
        def enum_cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if len(title) > 1:
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        pname  = psutil.Process(pid).name()
                    except:
                        pname = "?"
                    label = f"[{pname}] {title[:60]}"
                    self._window_map[label] = hwnd
        win32gui.EnumWindows(enum_cb, None)
        items = sorted(self._window_map.keys(), key=str.lower)
        self.proc_combo["values"] = items
        for item in items:
            if "wakfu" in item.lower():
                self.proc_combo.set(item)
                self._on_proc_selected(None)
                break

    def _on_proc_selected(self, event):
        sel = self.proc_var.get()
        if sel in self._window_map:
            self.selected_hwnd = self._window_map[sel]
            self.status_lbl.config(text=f"✓ {sel[:55]}", fg=C["green"])
            self._log(f"Fenêtre : {sel}")

    # ══════════════════════════════════════════════════════
    # CAPTURE + VARIANTS
    # ══════════════════════════════════════════════════════
    def _grab_clipboard(self):
        try:
            img = ImageGrab.grabclipboard()
            if img is None or isinstance(img, list):
                self._log("Pas d'image dans le presse-papier", "error"); return
            self.last_clipboard_img = img
            self.last_clipboard_cv  = pil_to_cv(img)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            img.save(os.path.join(CAPTURES_DIR, f"cap_{ts}.png"))
            thumb = img.copy()
            thumb.thumbnail((300,190))
            self._preview_photo = ImageTk.PhotoImage(thumb)
            self.preview_lbl.config(image=self._preview_photo, text="")
            match = self._try_recognize(self.last_clipboard_cv)
            if match:
                self.name_var.set(match["name"])
                folder_cat = match.get("category","")
                if folder_cat:
                    current = list(self.cat_combo["values"]) if self.cat_combo["values"] else []
                    if folder_cat not in current:
                        current.append(folder_cat)
                        self.cat_combo["values"] = current
                    self.cat_var.set(folder_cat)
                raw_type = match.get("type","")
                tpl_cat  = match.get("tpl_category","")
                tpl_type = match.get("tpl_type","")
                if not tpl_cat and " : " in raw_type:
                    tpl_cat, tpl_type = raw_type.split(" : ",1)
                if tpl_cat and hasattr(self,"tpl_cat_var"):
                    if tpl_cat not in CATEGORY_LIST:
                        CATEGORIES[tpl_cat] = []
                        CATEGORY_LIST.append(tpl_cat)
                        self.tpl_cat_combo["values"] = CATEGORY_LIST
                    self.tpl_cat_var.set(tpl_cat)
                    self._on_tpl_cat_changed()
                if tpl_type:
                    current_types = list(self.type_combo["values"]) if self.type_combo["values"] else []
                    if tpl_type not in current_types:
                        current_types.append(tpl_type)
                        self.type_combo["values"] = current_types
                    self.type_var.set(tpl_type)
                score = match.get("_score",0)
                self.auto_lbl.config(text=f"↳ Reconnu : {match['name']} ({folder_cat}) [{score:.0%}]")
            else:
                self.auto_lbl.config(text="")
            self._log(f"Capture : {img.width}x{img.height}", "ok")
        except Exception as e:
            self._log(f"Erreur capture : {e}", "error")

    def _try_recognize(self, cv_img):
        if cv_img is None: return None
        best_match, best_score = None, 0.0
        for tid, cv_list in self.template_cache.items():
            for cached_cv in cv_list:
                score = compare_images_multi(cv_img, cached_cv)
                if score > best_score and score >= 0.6:
                    best_score = score
                    best_match = self.config["templates"].get(tid,{})
        if best_match:
            best_match = dict(best_match)
            best_match["_score"] = best_score
        return best_match

    def _on_name_typing(self, event):
        typed = self.name_var.get()
        if not typed:
            self.suggestion_lbl.config(text=""); self._current_suggestion = ""; return
        typed_lower = typed.lower()
        all_names = list(set(
            self.config.get("name_history",[]) +
            [m["name"] for m in self.config["templates"].values()]
        ))
        matches = [n for n in all_names if n.lower().startswith(typed_lower) and n.lower()!=typed_lower]
        if matches:
            freq = Counter(self.config.get("name_history",[]))
            matches.sort(key=lambda n: freq.get(n,0), reverse=True)
            self.suggestion_lbl.config(text=f"Tab → {matches[0]}")
            self._current_suggestion = matches[0]
        else:
            self.suggestion_lbl.config(text=""); self._current_suggestion = ""

    def _accept_suggestion(self, event):
        if self._current_suggestion:
            self.name_var.set(self._current_suggestion)
            self.name_entry.icursor(tk.END)
            self.suggestion_lbl.config(text=""); self._current_suggestion = ""
        return "break"

    def _save_template(self):
        if self.last_clipboard_img is None:
            self._log("Colle d'abord une image (F5)", "error"); return
        name = self.name_var.get().strip()
        if not name:
            self._log("Donne un nom", "error"); return
        category = self.cat_var.get().strip()
        if not category:
            self._log("Choisis une catégorie", "error"); return
        tpl_cat  = self.tpl_cat_var.get() if hasattr(self,"tpl_cat_var") else ""
        tpl_type = self.type_var.get() if self.type_var.get()!="(aucun)" else ""
        ttype    = f"{tpl_cat} : {tpl_type}" if tpl_type else tpl_cat
        cat_dir  = os.path.join(LIBRARY_DIR, category)
        os.makedirs(cat_dir, exist_ok=True)
        if category not in self.config["categories"]:
            self.config["categories"].append(category)
            self._refresh_category_combos()
        safe    = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name)
        tpl_dir = os.path.join(cat_dir, safe)
        os.makedirs(tpl_dir, exist_ok=True)
        existing = glob.glob(os.path.join(tpl_dir,"*.png"))
        idx   = len(existing)
        fpath = os.path.join(tpl_dir, f"{safe}_v{idx}.png")
        self.last_clipboard_img.save(fpath)
        tid = f"{category}/{safe}"
        if tid not in self.config["templates"]:
            self.config["templates"][tid] = {
                "name":name,"type":ttype,"tpl_category":tpl_cat,
                "tpl_type":tpl_type,"category":category,
                "folder":safe,"variant_count":1,
            }
        else:
            self.config["templates"][tid]["variant_count"] = idx+1
        history = self.config.get("name_history",[])
        history.append(name)
        if len(history) > 500: history = history[-500:]
        self.config["name_history"] = history
        save_config(self.config)
        if tid not in self.template_cache: self.template_cache[tid] = []
        self.template_cache[tid].append(pil_to_cv(self.last_clipboard_img))
        self.last_clipboard_img = None; self.last_clipboard_cv = None
        self.name_var.set("")
        self.preview_lbl.config(image="", text="✓ Sauvegardé")
        self._preview_photo = None; self.auto_lbl.config(text="")
        self._refresh_library_view(); self._refresh_template_combos()
        n_variants = self.config["templates"][tid].get("variant_count",1)
        self._log(f"Sauvé : {name} → {category} ({ttype}) [{n_variants} variante(s)]","ok")

    def _add_variant(self):
        if self.last_clipboard_img is None:
            self._log("Colle d'abord une image (F5)", "error"); return
        name     = self.name_var.get().strip()
        category = self.cat_var.get().strip()
        if not name or not category:
            self._log("Choisis nom et catégorie du template existant", "error"); return
        safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name)
        tid  = f"{category}/{safe}"
        if tid not in self.config["templates"]:
            self._log(f"Template '{name}' introuvable. Utilise 'Nouveau'.", "warn"); return
        tpl_dir  = os.path.join(LIBRARY_DIR, category, safe)
        os.makedirs(tpl_dir, exist_ok=True)
        existing = glob.glob(os.path.join(tpl_dir,"*.png"))
        idx   = len(existing)
        fpath = os.path.join(tpl_dir, f"{safe}_v{idx}.png")
        self.last_clipboard_img.save(fpath)
        self.config["templates"][tid]["variant_count"] = idx+1
        save_config(self.config)
        if tid not in self.template_cache: self.template_cache[tid] = []
        self.template_cache[tid].append(pil_to_cv(self.last_clipboard_img))
        self.last_clipboard_img = None; self.last_clipboard_cv = None
        self.preview_lbl.config(image="", text="✓ Variante ajoutée")
        self._preview_photo = None; self.auto_lbl.config(text="")
        self._refresh_library_view()
        self._log(f"Variante #{idx+1} ajoutée à {name} [{category}]","ok")

    # ══════════════════════════════════════════════════════
    # LIBRARY
    # ══════════════════════════════════════════════════════
    def _load_library(self):
        self.template_cache = {}
        if os.path.exists(LIBRARY_DIR):
            for cat_name in os.listdir(LIBRARY_DIR):
                cat_path = os.path.join(LIBRARY_DIR, cat_name)
                if not os.path.isdir(cat_path): continue
                if cat_name not in self.config["categories"]:
                    self.config["categories"].append(cat_name)
                for item_name in os.listdir(cat_path):
                    item_path = os.path.join(cat_path, item_name)
                    if os.path.isdir(item_path):
                        tid     = f"{cat_name}/{item_name}"
                        cv_list = []
                        for img_file in sorted(glob.glob(os.path.join(item_path,"*.png"))):
                            try: cv_list.append(pil_to_cv(Image.open(img_file)))
                            except: pass
                        if cv_list: self.template_cache[tid] = cv_list
                        if tid not in self.config["templates"]:
                            self.config["templates"][tid] = {
                                "name":item_name,"type":"ressource",
                                "category":cat_name,"folder":item_name,
                                "variant_count":len(cv_list),
                            }
                        else:
                            self.config["templates"][tid]["variant_count"] = len(cv_list)
                    elif item_name.lower().endswith((".png",".jpg",".bmp")):
                        base_name = os.path.splitext(item_name)[0]
                        safe      = "".join(c if c.isalnum() or c in "-_ " else "_" for c in base_name)
                        new_dir   = os.path.join(cat_path, safe)
                        os.makedirs(new_dir, exist_ok=True)
                        new_path  = os.path.join(new_dir, f"{safe}_v0.png")
                        if not os.path.exists(new_path): shutil.move(item_path, new_path)
                        else: os.remove(item_path)
                        tid = f"{cat_name}/{safe}"
                        try:
                            self.template_cache[tid] = [pil_to_cv(Image.open(new_path))]
                        except:
                            self.template_cache[tid] = []
                        old_tid  = f"{cat_name}/{item_name}"
                        old_meta = self.config["templates"].pop(old_tid,{})
                        if tid not in self.config["templates"]:
                            self.config["templates"][tid] = {
                                "name":old_meta.get("name",base_name),
                                "type":old_meta.get("type","ressource"),
                                "category":cat_name,"folder":safe,"variant_count":1,
                            }
        save_config(self.config)
        self._refresh_category_combos()
        self._refresh_library_view()
        self._refresh_template_combos()
        self._refresh_seq_tree()
        if hasattr(self,"cat_combo"):
            self.cat_combo["values"] = self.config.get("categories",[])
        total_variants = sum(len(v) for v in self.template_cache.values())
        self._log(f"Chargé : {len(self.template_cache)} templates ({total_variants} images), "
                  f"{len(self.config['categories'])} catégories","ok")

    def _refresh_category_combos(self):
        cats = self.config.get("categories",[])
        self.cat_combo["values"] = cats
        flat = []
        for cat_name, cat_types in CATEGORIES.items():
            for t in cat_types: flat.append(f"{cat_name} : {t}")
            if not cat_types: flat.append(cat_name)
        self.filter_combo["values"] = ["Tout"] + flat + ["───"] + cats

    def _refresh_template_combos(self):
        names = []
        self._tpl_name_to_tid = {}
        for tid, meta in self.config["templates"].items():
            n_var = meta.get("variant_count",1)
            key   = f"{meta['name']}  ·  {meta['category']}  ({n_var})"
            names.append(key)
            self._tpl_name_to_tid[key] = tid
        names.sort()
        self.step_template_combo["values"] = ["(aucun)"] + names
        if hasattr(self,"cond_template_combo"):
            self.cond_template_combo["values"] = ["(aucun)"] + names

    def _refresh_library_view(self):
        self.lib_tree.delete(*self.lib_tree.get_children())
        filt = self.filter_var.get()
        for tid, meta in self.config["templates"].items():
            if filt != "Tout":
                if filt not in ("---","───") and meta.get("category") != filt:
                    continue
            cat     = meta.get("category","?")
            folder  = meta.get("folder","")
            tpl_dir = os.path.join(LIBRARY_DIR, cat, folder)
            n_var   = meta.get("variant_count",0)
            sz = ""
            if os.path.isdir(tpl_dir):
                total = sum(os.path.getsize(os.path.join(tpl_dir,f))
                            for f in os.listdir(tpl_dir) if f.endswith(".png"))
                sz = f"{total/1024:.1f}KB"
            self.lib_tree.insert("","end", iid=tid,
                                 values=(meta.get("name","?"), meta.get("type","?"),
                                         cat, f"{n_var} img", sz))

    def _on_lib_select(self, event):
        sel = self.lib_tree.selection()
        if not sel: return
        meta   = self.config["templates"].get(sel[0],{})
        folder = meta.get("folder","")
        tpl_dir = os.path.join(LIBRARY_DIR, meta.get("category",""), folder)
        for w in self.lib_preview_frame.winfo_children(): w.destroy()
        self._lib_variant_photos = []
        if os.path.isdir(tpl_dir):
            for img_path in sorted(glob.glob(os.path.join(tpl_dir,"*.png")))[:4]:
                try:
                    img   = Image.open(img_path)
                    thumb = img.copy(); thumb.thumbnail((50,50))
                    photo = ImageTk.PhotoImage(thumb)
                    self._lib_variant_photos.append(photo)
                    tk.Label(self.lib_preview_frame, image=photo, bg=C["surface"]).pack(side="left",padx=2)
                except: pass
        n_var = meta.get("variant_count",0)
        self.lib_info_lbl.config(
            text=f"{meta.get('name','')}  |  {meta.get('type','')}  |  "
                 f"{meta.get('category','')}  |  {n_var} variante(s)")

    def _add_category(self):
        name = simpledialog.askstring("Catégorie","Nom :", parent=self.root)
        if name and name.strip():
            name = name.strip()
            os.makedirs(os.path.join(LIBRARY_DIR,name), exist_ok=True)
            if name not in self.config["categories"]:
                self.config["categories"].append(name)
                save_config(self.config)
            self._refresh_category_combos()
            self._log(f"Catégorie : {name}","ok")

    def _rename_selected(self):
        sel = self.lib_tree.selection()
        if not sel: return
        tid  = sel[0]
        meta = self.config["templates"].get(tid)
        if not meta: return
        new_name = simpledialog.askstring("Renommer","Nom :", parent=self.root,
                                           initialvalue=meta["name"])
        if not new_name or not new_name.strip(): return
        new_name  = new_name.strip()
        cat       = meta["category"]
        old_folder= meta.get("folder","")
        old_dir   = os.path.join(LIBRARY_DIR, cat, old_folder)
        safe      = "".join(c if c.isalnum() or c in "-_ " else "_" for c in new_name)
        new_dir   = os.path.join(LIBRARY_DIR, cat, safe)
        if os.path.isdir(old_dir) and old_dir != new_dir: os.rename(old_dir, new_dir)
        del self.config["templates"][tid]
        new_tid = f"{cat}/{safe}"
        meta["name"] = new_name; meta["folder"] = safe
        self.config["templates"][new_tid] = meta
        if tid in self.template_cache: self.template_cache[new_tid] = self.template_cache.pop(tid)
        self._update_seq_template_refs(tid, new_tid)
        save_config(self.config)
        self._refresh_library_view(); self._refresh_template_combos()
        self._log(f"Renommé : {new_name}","ok")

    def _move_selected(self):
        sel = self.lib_tree.selection()
        if not sel: return
        tid  = sel[0]; meta = self.config["templates"].get(tid)
        if not meta: return
        cats = self.config["categories"]
        win  = tk.Toplevel(self.root); win.title("Déplacer")
        win.geometry("300x130"); win.configure(bg=C["bg"])
        tk.Label(win, text=f"'{meta['name']}' vers:", bg=C["bg"], fg=C["text"]).pack(pady=8)
        mv = tk.StringVar()
        ttk.Combobox(win, textvariable=mv, values=cats, state="readonly", width=25).pack(pady=4)
        def do():
            nc = mv.get()
            if not nc: return
            folder  = meta.get("folder","")
            old_dir = os.path.join(LIBRARY_DIR, meta["category"], folder)
            os.makedirs(os.path.join(LIBRARY_DIR,nc), exist_ok=True)
            new_dir = os.path.join(LIBRARY_DIR, nc, folder)
            if os.path.isdir(old_dir): shutil.move(old_dir, new_dir)
            del self.config["templates"][tid]
            new_tid = f"{nc}/{folder}"; meta["category"] = nc
            self.config["templates"][new_tid] = meta
            if tid in self.template_cache: self.template_cache[new_tid] = self.template_cache.pop(tid)
            self._update_seq_template_refs(tid, new_tid)
            save_config(self.config); self._refresh_library_view(); self._refresh_template_combos()
            win.destroy()
        tk.Button(win, text="OK", bg=C["green"], fg="white", relief="flat", command=do).pack(pady=8)

    def _change_type_selected(self):
        sel = self.lib_tree.selection()
        if not sel: return
        meta = self.config["templates"].get(sel[0])
        if not meta: return
        win = tk.Toplevel(self.root); win.title("Type")
        win.geometry("320x150"); win.configure(bg=C["bg"])
        tv = tk.StringVar(value=meta.get("type",""))
        ttk.Combobox(win, textvariable=tv, state="readonly", width=30,
                     values=ALL_FLAT_TYPES).pack(pady=16)
        def do():
            meta["type"] = tv.get(); save_config(self.config)
            self._refresh_library_view(); self._refresh_template_combos(); win.destroy()
        tk.Button(win, text="OK", bg=C["green"], fg="white", relief="flat", command=do).pack(pady=8)

    def _delete_selected(self):
        sel = self.lib_tree.selection()
        if not sel: return
        meta = self.config["templates"].get(sel[0])
        if not meta: return
        n_var = meta.get("variant_count",0)
        if not messagebox.askyesno("Confirmer", f"Supprimer '{meta['name']}' ({n_var} variante(s)) ?"): return
        folder  = meta.get("folder","")
        tpl_dir = os.path.join(LIBRARY_DIR, meta["category"], folder)
        if os.path.isdir(tpl_dir): shutil.rmtree(tpl_dir)
        del self.config["templates"][sel[0]]
        self.template_cache.pop(sel[0], None)
        save_config(self.config); self._refresh_library_view(); self._refresh_template_combos()

    def _sort_tree(self, col):
        rev   = self._sort_reverse.get(col, False)
        items = [(self.lib_tree.set(k,col),k) for k in self.lib_tree.get_children("")]
        items.sort(reverse=rev)
        for i,(_,k) in enumerate(items): self.lib_tree.move(k,"",i)
        self._sort_reverse[col] = not rev

    # ══════════════════════════════════════════════════════
    # SEQUENCES
    # ══════════════════════════════════════════════════════
    def _get_seq_by_id(self, sid, seqs=None):
        if seqs is None: seqs = self.config["sequences"]
        for s in seqs:
            if s.get("id") == sid: return s
            found = self._get_seq_by_id(sid, s.get("children",[]))
            if found: return found
        return None

    def _get_seq_parent_list(self, sid, seqs=None):
        if seqs is None: seqs = self.config["sequences"]
        for i,s in enumerate(seqs):
            if s.get("id") == sid: return seqs, i
            result = self._get_seq_parent_list(sid, s.get("children",[]))
            if result: return result
        return None

    def _next_seq_id(self):
        max_id = [0]
        def walk(seqs):
            for s in seqs:
                if s.get("id",0) > max_id[0]: max_id[0] = s["id"]
                walk(s.get("children",[]))
        walk(self.config["sequences"]); return max_id[0]+1

    def _ensure_seq_ids(self):
        counter = [0]
        def walk(seqs):
            for s in seqs:
                if "id" not in s: counter[0]+=1; s["id"]=counter[0]+1000
                if "children"   not in s: s["children"]   = []
                if "conditions" not in s: s["conditions"] = []
                walk(s["children"])
        walk(self.config["sequences"])

    def _refresh_seq_tree(self):
        self._ensure_seq_ids()
        self.seq_tree.delete(*self.seq_tree.get_children())
        def insert(seqs, parent=""):
            for s in seqs:
                sid      = str(s["id"])
                prefix   = "✓" if s.get("enabled",True) else "✗"
                n_steps  = len(s.get("steps",[]))
                n_ch     = len(s.get("children",[]))
                n_conds  = len(s.get("conditions",[]))
                label    = f"{prefix} {s['name']} ({n_steps}étapes"
                if n_conds: label += f", {n_conds}cond"
                if n_ch:    label += f", {n_ch}enfants"
                label += ")"
                tag = "enabled" if s.get("enabled",True) else "disabled"
                self.seq_tree.insert(parent,"end",iid=sid,text=label,tags=(tag,))
                insert(s.get("children",[]),sid)
        insert(self.config["sequences"])
        if self._active_seq_idx is not None:
            try:
                self.seq_tree.selection_set(str(self._active_seq_idx))
                self.seq_tree.see(str(self._active_seq_idx))
            except: pass
        all_names = []
        def walk_names(seqs, prefix=""):
            for s in seqs:
                all_names.append((s["id"], f"{prefix}{s['name']}"))
                walk_names(s.get("children",[]), prefix+"  ")
        walk_names(self.config["sequences"])
        self.step_subseq_combo["values"] = [f"[{sid}] {n}" for sid,n in all_names]

    def _on_seq_tree_select(self, event):
        sel = self.seq_tree.selection()
        if not sel: return
        sid = int(sel[0]); self._active_seq_idx = sid
        seq = self._get_seq_by_id(sid)
        if not seq: return
        self.seq_enabled_var.set(seq.get("enabled",True))
        self.seq_name_lbl.config(text=f"▶ {seq['name']}")
        self._refresh_conditions_list(seq)
        self._refresh_steps_list(seq)

    def _get_active_seq(self):
        if self._active_seq_idx is None: return None
        return self._get_seq_by_id(self._active_seq_idx)

    def _refresh_steps_list(self, seq):
        self.steps_listbox.delete(0, tk.END)
        for i, step in enumerate(seq.get("steps",[])):
            stype    = step.get("type","?")
            label    = STEP_DICT.get(stype, stype)
            tpl_tid  = step.get("template","")
            tpl_name = ""
            if tpl_tid:
                meta     = self.config["templates"].get(tpl_tid,{})
                tpl_name = f" → {meta.get('name','?')} [{meta.get('category','')}]"
            val      = step.get("value","")
            val_str  = f" ({val})" if val else ""
            sub_info = ""
            if stype in ("sous_sequence","si_detecte_alors","si_absent_alors"):
                sub_id  = step.get("sub_sequence_id")
                if sub_id:
                    sub_seq  = self._get_seq_by_id(sub_id)
                    sub_info = f" ⇒ [{sub_seq['name']}]" if sub_seq else f" ⇒ [?id={sub_id}]"
            slot_info = ""
            if stype == "bind_slot" and val:
                key = SLOT_KEYS.get(val.strip(), val)
                slot_info = f" [touche: {key}]"
            self.steps_listbox.insert(tk.END,
                f"  {i+1}. {label}{tpl_name}{sub_info}{slot_info}{val_str}")

    def _add_sequence(self):
        name = simpledialog.askstring("Nouvelle séquence","Nom :", parent=self.root)
        if not name or not name.strip(): return
        seq = {"id":self._next_seq_id(),"name":name.strip(),
               "enabled":True,"steps":[],"children":[],"conditions":[]}
        self.config["sequences"].append(seq)
        save_config(self.config); self._active_seq_idx = seq["id"]
        self._refresh_seq_tree(); self._log(f"Séquence : {name}","ok")

    def _add_child_sequence(self):
        parent_seq = self._get_active_seq()
        if not parent_seq: self._log("Sélectionne une séquence parente","warn"); return
        name = simpledialog.askstring("Sous-séquence","Nom :", parent=self.root)
        if not name or not name.strip(): return
        child = {"id":self._next_seq_id(),"name":name.strip(),
                 "enabled":True,"steps":[],"children":[],"conditions":[]}
        parent_seq["children"].append(child)
        save_config(self.config); self._active_seq_idx = child["id"]
        self._refresh_seq_tree(); self._log(f"Sous-séquence : {name}","ok")

    def _rename_sequence(self):
        seq = self._get_active_seq()
        if not seq: return
        name = simpledialog.askstring("Renommer","Nom :", parent=self.root,
                                       initialvalue=seq["name"])
        if name and name.strip():
            seq["name"] = name.strip(); save_config(self.config); self._refresh_seq_tree()

    def _delete_sequence(self):
        seq = self._get_active_seq()
        if not seq: return
        if not messagebox.askyesno("Confirmer", f"Supprimer '{seq['name']}' et ses enfants ?"): return
        result = self._get_seq_parent_list(seq["id"])
        if result: lst,idx = result; lst.pop(idx)
        self._active_seq_idx = None; save_config(self.config); self._refresh_seq_tree()
        self.steps_listbox.delete(0,tk.END)
        self.seq_name_lbl.config(text="← Sélectionne une séquence")

    def _toggle_seq_enabled(self):
        seq = self._get_active_seq()
        if not seq: return
        seq["enabled"] = self.seq_enabled_var.get()
        save_config(self.config); self._refresh_seq_tree()

    def _move_seq_up(self):
        seq = self._get_active_seq()
        if not seq: return
        result = self._get_seq_parent_list(seq["id"])
        if not result: return
        lst,idx = result
        if idx > 0: lst[idx],lst[idx-1]=lst[idx-1],lst[idx]; save_config(self.config); self._refresh_seq_tree()

    def _move_seq_down(self):
        seq = self._get_active_seq()
        if not seq: return
        result = self._get_seq_parent_list(seq["id"])
        if not result: return
        lst,idx = result
        if idx<len(lst)-1: lst[idx],lst[idx+1]=lst[idx+1],lst[idx]; save_config(self.config); self._refresh_seq_tree()

    def _copy_sequence(self):
        seq = self._get_active_seq()
        if not seq: return
        copy = deepcopy(seq)
        def reassign_ids(s):
            s["id"] = self._next_seq_id(); s["name"] = s["name"]+" (copie)"
            for ch in s.get("children",[]): reassign_ids(ch)
        reassign_ids(copy)
        result = self._get_seq_parent_list(seq["id"])
        if result: lst,idx=result; lst.insert(idx+1,copy)
        else: self.config["sequences"].append(copy)
        save_config(self.config); self._active_seq_idx = copy["id"]
        self._refresh_seq_tree(); self._log(f"Copié : {copy['name']}","ok")

    def _update_seq_template_refs(self, old_tid, new_tid):
        def walk(seqs):
            for s in seqs:
                for step in s.get("steps",[]):
                    if step.get("template")==old_tid: step["template"]=new_tid
                walk(s.get("children",[]))
        walk(self.config["sequences"])

    # ── Conditions ──
    def _refresh_conditions_list(self, seq):
        self.cond_listbox.delete(0, tk.END)
        for i,cond in enumerate(seq.get("conditions",[])):
            tpl_tid  = cond.get("template","")
            meta     = self.config["templates"].get(tpl_tid,{})
            mode     = cond.get("mode","absent")
            mode_lbl = "est ABSENT" if mode=="absent" else "est PRÉSENT"
            self.cond_listbox.insert(tk.END,
                f"  {i+1}. {meta.get('name','?')} [{meta.get('category','')}] {mode_lbl}")

    def _add_condition(self):
        seq = self._get_active_seq()
        if not seq: self._log("Sélectionne une séquence","warn"); return
        tpl_display = self.cond_template_var.get()
        if not tpl_display or tpl_display=="(aucun)":
            self._log("Choisis un template pour la condition","warn"); return
        tpl_tid = self._tpl_name_to_tid.get(tpl_display,"")
        if not tpl_tid: self._log("Template introuvable","error"); return
        mode_display = self.cond_mode_var.get()
        mode = "absent" if "absent" in mode_display else "present"
        if "conditions" not in seq: seq["conditions"] = []
        seq["conditions"].append({"template":tpl_tid,"mode":mode})
        save_config(self.config); self._refresh_conditions_list(seq)
        meta = self.config["templates"].get(tpl_tid,{})
        self._log(f"Condition : {meta.get('name','?')} {mode_display}","ok")

    def _delete_condition(self):
        seq = self._get_active_seq()
        if not seq: return
        sel = self.cond_listbox.curselection()
        if not sel: return
        seq.get("conditions",[]).pop(sel[0])
        save_config(self.config); self._refresh_conditions_list(seq)

    def _check_conditions(self, seq, det_map):
        for cond in seq.get("conditions",[]):
            tpl_tid     = cond.get("template","")
            mode        = cond.get("mode","absent")
            is_detected = tpl_tid in det_map and len(det_map[tpl_tid]) > 0
            if mode=="absent"  and is_detected:  return False
            if mode=="present" and not is_detected: return False
        return True

    # ── Steps ──
    def _on_step_type_changed(self, event=None):
        raw   = self.step_type_var.get()
        stype = ""
        for key,label in STEP_TYPES:
            if label in raw: stype=key; break
        if stype in ("sous_sequence","si_detecte_alors","si_absent_alors"):
            self.step_subseq_frame.pack(fill="x", padx=6, pady=2)
        else:
            self.step_subseq_frame.pack_forget()
        self._update_value_hint()

    def _on_key_picked(self, event=None):
        key = self.key_picker_var.get()
        if key and not key.startswith("──"): self.step_value_var.set(key)

    def _capture_key_press(self):
        self.capture_key_btn.config(text="⏳ Appuie...", bg=C["yellow"], fg=C["bg"])
        self.root.update()
        def on_key(e):
            if e.name:
                self.step_value_var.set(e.name)
                self.root.after(0, lambda: self.capture_key_btn.config(
                    text="🎹 Capturer", bg=C["surface2"], fg=C["text"]))
            try: keyboard.unhook(hook)
            except: pass
        try:
            hook = keyboard.on_press(on_key)
            def timeout():
                try: keyboard.unhook(hook)
                except: pass
                self.capture_key_btn.config(text="🎹 Capturer", bg=C["surface2"], fg=C["text"])
            self.root.after(5000, timeout)
        except Exception as e:
            self._log(f"Capture touche : {e}","error")
            self.capture_key_btn.config(text="🎹 Capturer", bg=C["surface2"], fg=C["text"])

    def _update_value_hint(self):
        raw   = self.step_type_var.get()
        stype = ""
        for key,label in STEP_TYPES:
            if label in raw: stype=key; break
        hints = {
            "wait":"Durée en ms (ex: 500)","touche":"Touche à presser",
            "combo_touches":"Ex: ctrl+c, alt+F4","bind_slot":"Numéro du slot (1-9)",
            "clic_position":"x,y en pixels (ex: 400,300)","clic_grille":"col,row (ex: 3,5)",
            "attendre_detection":"Timeout en ms (ex: 5000)",
            "attendre_disparition":"Timeout en ms (ex: 5000)",
        }
        self.step_value_hint.config(text=hints.get(stype,""))

    def _add_step(self):
        seq = self._get_active_seq()
        if not seq: self._log("Sélectionne une séquence","warn"); return
        stype    = parse_step_type(self.step_type_var.get())
        tpl_name = self.step_template_var.get()
        tpl_tid  = self._tpl_name_to_tid.get(tpl_name,"") if tpl_name and tpl_name!="(aucun)" else ""
        val      = self.step_value_var.get().strip()
        step     = {"type":stype,"template":tpl_tid,"value":val}
        if stype in ("sous_sequence","si_detecte_alors","si_absent_alors"):
            sub_str = self.step_subseq_var.get()
            if sub_str:
                try: step["sub_sequence_id"] = int(sub_str.split("]")[0].replace("[",""))
                except: pass
        seq["steps"].append(step)
        save_config(self.config); self._refresh_steps_list(seq); self._refresh_seq_tree()

    def _edit_step(self):
        seq = self._get_active_seq()
        if not seq: return
        sel = self.steps_listbox.curselection()
        if not sel: return
        idx  = sel[0]; step = seq["steps"][idx]
        stype    = parse_step_type(self.step_type_var.get())
        tpl_name = self.step_template_var.get()
        tpl_tid  = self._tpl_name_to_tid.get(tpl_name,"") if tpl_name and tpl_name!="(aucun)" else ""
        val      = self.step_value_var.get().strip()
        step["type"]=stype; step["template"]=tpl_tid; step["value"]=val
        if stype in ("sous_sequence","si_detecte_alors","si_absent_alors"):
            sub_str = self.step_subseq_var.get()
            if sub_str:
                try: step["sub_sequence_id"] = int(sub_str.split("]")[0].replace("[",""))
                except: pass
        save_config(self.config); self._refresh_steps_list(seq); self._refresh_seq_tree()
        self._log(f"Étape {idx+1} modifiée","ok")

    def _delete_step(self):
        seq = self._get_active_seq()
        if not seq: return
        sel = self.steps_listbox.curselection()
        if not sel: return
        seq["steps"].pop(sel[0]); save_config(self.config)
        self._refresh_steps_list(seq); self._refresh_seq_tree()

    def _move_step_up(self):
        seq = self._get_active_seq()
        if not seq: return
        sel = self.steps_listbox.curselection()
        if not sel or sel[0]==0: return
        i = sel[0]; seq["steps"][i],seq["steps"][i-1]=seq["steps"][i-1],seq["steps"][i]
        save_config(self.config); self._refresh_steps_list(seq); self.steps_listbox.selection_set(i-1)

    def _move_step_down(self):
        seq = self._get_active_seq()
        if not seq: return
        sel = self.steps_listbox.curselection()
        if not sel or sel[0]>=len(seq["steps"])-1: return
        i = sel[0]; seq["steps"][i],seq["steps"][i+1]=seq["steps"][i+1],seq["steps"][i]
        save_config(self.config); self._refresh_steps_list(seq); self.steps_listbox.selection_set(i+1)

    def _copy_step(self):
        seq = self._get_active_seq()
        if not seq: return
        sel = self.steps_listbox.curselection()
        if not sel: return
        step_copy = deepcopy(seq["steps"][sel[0]])
        seq["steps"].insert(sel[0]+1, step_copy)
        save_config(self.config); self._refresh_steps_list(seq)

    # ══════════════════════════════════════════════════════
    # CALIBRATION
    # ══════════════════════════════════════════════════════
    def _calib_capture(self):
        if not self.selected_hwnd or not win32gui.IsWindow(self.selected_hwnd):
            self._log("Sélectionne d'abord une fenêtre","error"); return
        img = capture_window(self.selected_hwnd)
        if img is None: self._log("Capture échouée","error"); return
        self._calib_img = img; self._calib_redraw()
        self._log(f"Calibration : capture {img.width}x{img.height}","ok")

    def _calib_redraw(self, event=None):
        if self._calib_img is None: return
        cw = self.calib_canvas.winfo_width(); ch = self.calib_canvas.winfo_height()
        if cw<10 or ch<10: return
        iw,ih = self._calib_img.size
        scale  = min(cw/iw, ch/ih); nw=int(iw*scale); nh=int(ih*scale)
        self._calib_scale  = scale
        ox=(cw-nw)//2; oy=(ch-nh)//2; self._calib_offset=(ox,oy)
        resized = self._calib_img.resize((nw,nh), Image.LANCZOS)
        overlay = resized.copy(); draw = ImageDraw.Draw(overlay)
        colors  = ["#ff4444","#44ff44","#4488ff","#ff44ff","#ffaa00"]; r=10
        for i,(px,py) in enumerate(self._calib_points):
            cx=int(px*scale); cy=int(py*scale); col=colors[i%len(colors)]
            for rr in range(r+6,r,-1):
                draw.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],outline=col,width=1)
            draw.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col,outline="white",width=2)
            draw.line([cx-18,cy,cx+18,cy],fill=col,width=1)
            draw.line([cx,cy-18,cx,cy+18],fill=col,width=1)
            draw.text((cx+r+5,cy-8),f"P{i+1} ({int(px)},{int(py)})",fill="white")
        if len(self._calib_points)>=2:
            for i in range(len(self._calib_points)-1):
                x1,y1=self._calib_points[i]; x2,y2=self._calib_points[i+1]
                draw.line([int(x1*scale),int(y1*scale),int(x2*scale),int(y2*scale)],
                           fill="#ffffff80",width=1)
        self._draw_grid_overlay(draw,nw,nh,scale)
        grid=self.config.get("grid",{})
        gox=int(grid.get("origin_x",0)*scale); goy=int(grid.get("origin_y",0)*scale)
        if 0<=gox<nw and 0<=goy<nh:
            draw.ellipse([gox-6,goy-6,gox+6,goy+6],fill="#ff0",outline="white",width=2)
            draw.text((gox+8,goy-8),"GRID(0,0)",fill="#ff0")
        self._calib_photo = ImageTk.PhotoImage(overlay)
        self.calib_canvas.delete("all")
        self.calib_canvas.create_image(ox,oy,anchor="nw",image=self._calib_photo)
        n=len(self._calib_points)
        self.calib_info_lbl.config(
            text=f"{n} point{'s' if n!=1 else ''} — "
                 "Clic=ajouter  Glisser=déplacer  Double-clic=tester  Clic-droit=supprimer")

    def _canvas_to_img(self,cx,cy):
        ox,oy=self._calib_offset
        return (cx-ox)/self._calib_scale,(cy-oy)/self._calib_scale

    def _find_nearest_point(self,img_x,img_y,max_dist=20):
        best_i=None; best_d=max_dist/self._calib_scale if self._calib_scale>0 else max_dist
        for i,(px,py) in enumerate(self._calib_points):
            d=((px-img_x)**2+(py-img_y)**2)**0.5
            if d<best_d: best_d=d; best_i=i
        return best_i

    def _calib_click(self,event):
        if self._calib_img is None: return
        img_x,img_y = self._canvas_to_img(event.x,event.y)
        iw,ih = self._calib_img.size
        if img_x<0 or img_y<0 or img_x>=iw or img_y>=ih: return
        if self._grid_origin_mode:
            self._grid_origin_mode = False
            self.grid_ox_var.set(int(img_x)); self.grid_oy_var.set(int(img_y))
            self._save_grid(); self._calib_redraw()
            self._log(f"Origine grille : ({int(img_x)}, {int(img_y)})","ok"); return
        nearest = self._find_nearest_point(img_x,img_y)
        if nearest is not None:
            self._calib_selected_pt=nearest; self._calib_dragging=True; return
        if len(self._calib_points)>=5:
            self._log("Max 5 points","warn"); return
        self._calib_points.append((img_x,img_y))
        self._calib_selected_pt=len(self._calib_points)-1
        self._calib_dragging=False; self._calib_redraw()
        self._log(f"Point P{len(self._calib_points)}: ({int(img_x)},{int(img_y)})","ok")

    def _calib_drag(self,event):
        if not self._calib_dragging or self._calib_selected_pt is None: return
        if self._calib_img is None: return
        img_x,img_y = self._canvas_to_img(event.x,event.y)
        iw,ih = self._calib_img.size
        img_x=max(0,min(img_x,iw-1)); img_y=max(0,min(img_y,ih-1))
        self._calib_points[self._calib_selected_pt]=(img_x,img_y)
        self._calib_redraw()

    def _calib_release(self,event):
        self._calib_dragging=False

    def _calib_double_click(self,event):
        if self._calib_img is None: return
        img_x,img_y = self._canvas_to_img(event.x,event.y)
        nearest = self._find_nearest_point(img_x,img_y,max_dist=30)
        if nearest is not None:
            px,py = self._calib_points[nearest]
            coords = self._img_to_screen(px,py)
            if coords:
                win32api.SetCursorPos(coords)
                self._log(f"Test P{nearest+1} : souris → ({coords[0]},{coords[1]})","ok")
        else:
            coords = self._img_to_screen(img_x,img_y)
            if coords: win32api.SetCursorPos(coords)

    def _calib_delete_point(self,event):
        if self._calib_img is None: return
        img_x,img_y = self._canvas_to_img(event.x,event.y)
        nearest = self._find_nearest_point(img_x,img_y,max_dist=30)
        if nearest is not None:
            self._calib_points.pop(nearest)
            self._calib_selected_pt=None; self._calib_redraw()

    def _calib_clear(self):
        self._calib_points.clear()
        self._calib_selected_pt=None; self._calib_redraw()

    def _calib_test_all(self):
        if not self._calib_points: self._log("Aucun point","warn"); return
        def run():
            for i,(px,py) in enumerate(self._calib_points):
                coords = self._img_to_screen(px,py)
                if coords:
                    win32api.SetCursorPos(coords)
                    self.root.after(0,lambda ii=i,cc=coords:
                        self._log(f"Test P{ii+1} → ({cc[0]},{cc[1]})","ok"))
                time.sleep(1.0)
        threading.Thread(target=run,daemon=True).start()

    def _calib_save(self):
        if not self._calib_points: self._log("Aucun point","warn"); return
        points = []
        for px,py in self._calib_points:
            coords = self._img_to_screen(px,py)
            if coords:
                points.append({"img_x":int(px),"img_y":int(py),
                                "screen_x":coords[0],"screen_y":coords[1]})
        self.config["calibration_points"] = points
        self.config["calibration_offset_x"] = self.offset_x_var.get()
        self.config["calibration_offset_y"] = self.offset_y_var.get()
        save_config(self.config)
        self._log(f"Calibration sauvegardée ({len(points)} points) ✓","ok")

    def _img_to_screen(self,img_x,img_y):
        if not self.selected_hwnd or not win32gui.IsWindow(self.selected_hwnd): return None
        sx,sy = win32gui.ClientToScreen(self.selected_hwnd,(0,0))
        return (sx+int(img_x)+self.offset_x_var.get(),
                sy+int(img_y)+self.offset_y_var.get())

    def _save_grid(self):
        if "grid" not in self.config: self.config["grid"]={}
        self.config["grid"]["cell_w"]   = self.grid_cw_var.get()
        self.config["grid"]["cell_h"]   = self.grid_ch_var.get()
        self.config["grid"]["origin_x"] = self.grid_ox_var.get()
        self.config["grid"]["origin_y"] = self.grid_oy_var.get()
        self.config["grid"]["visible"]  = self.grid_visible_var.get()
        if hasattr(self,"grid_cols_var"): self.config["grid"]["cols"]=self.grid_cols_var.get()
        if hasattr(self,"grid_rows_var"): self.config["grid"]["rows"]=self.grid_rows_var.get()
        save_config(self.config); self._log("Grille sauvegardée","ok")

    def _on_grid_param_change(self):
        self._save_grid(); self._grid_canvas_redraw()

    def _grid_to_pixel(self,col,row):
        grid=self.config.get("grid",{})
        ox=grid.get("origin_x",0); oy=grid.get("origin_y",0)
        cw=grid.get("cell_w",43);  ch=grid.get("cell_h",22)
        px=ox+(col-row)*(cw//2);   py=oy+(col+row)*(ch//2)
        return int(px),int(py)

    def _pixel_to_grid(self,px,py):
        grid=self.config.get("grid",{})
        ox=grid.get("origin_x",0); oy=grid.get("origin_y",0)
        cw=grid.get("cell_w",43);  ch=grid.get("cell_h",22)
        if cw==0 or ch==0: return 0,0
        dx=px-ox; dy=py-oy
        col=(dx/(cw/2.0)+dy/(ch/2.0))/2.0
        row=(dy/(ch/2.0)-dx/(cw/2.0))/2.0
        return int(round(col)),int(round(row))

    def _draw_grid_overlay(self,draw,img_w,img_h,scale=1.0):
        grid=self.config.get("grid",{})
        if not grid.get("visible",False): return
        cols=grid.get("cols",20); rows=grid.get("rows",20)
        for c in range(-1,cols+1):
            for r in range(-1,rows+1):
                px,py=self._grid_to_pixel(c,r)
                px=int(px*scale); py=int(py*scale)
                cw=int(grid.get("cell_w",43)*scale)
                ch=int(grid.get("cell_h",22)*scale)
                hw,hh=cw//2,ch//2
                diamond=[(px,py-hh),(px+hw,py),(px,py+hh),(px-hw,py)]
                if all(0<=p[0]<img_w and 0<=p[1]<img_h for p in diamond):
                    draw.polygon(diamond,outline="#ffffff30")
                    if c%5==0 and r%5==0:
                        try: draw.text((px-8,py-6),f"{c},{r}",fill="#ffffff60")
                        except: pass

    def _save_offsets(self):
        self.config["calibration_offset_x"]=self.offset_x_var.get()
        self.config["calibration_offset_y"]=self.offset_y_var.get()
        save_config(self.config)

    def _reset_offsets(self):
        self.offset_x_var.set(0); self.offset_y_var.set(0); self._save_offsets()

    # ── Grid canvas ──
    def _grid_capture(self):
        if not self.selected_hwnd or not win32gui.IsWindow(self.selected_hwnd):
            self._log("Fenêtre invalide","error"); return
        ss = capture_window(self.selected_hwnd)
        if ss: self._grid_img=ss; self._grid_canvas_redraw(); self._log("Capture grille OK","ok")

    def _grid_canvas_click(self,event):
        if not hasattr(self,"_grid_img") or self._grid_img is None: return
        if self._grid_origin_mode:
            self._grid_origin_mode=False
            ix,iy=self._grid_canvas_to_img(event.x,event.y)
            self.grid_ox_var.set(int(ix)); self.grid_oy_var.set(int(iy))
            self._save_grid(); self._grid_canvas_redraw()
            self._log(f"Origine grille : ({int(ix)},{int(iy)})","ok"); return
        ix,iy=self._grid_canvas_to_img(event.x,event.y)
        col,row=self._pixel_to_grid(ix,iy)
        self.grid_info_lbl.config(text=f"Pixel: ({int(ix)},{int(iy)})  →  Case: ({col},{row})")

    def _grid_canvas_motion(self,event=None):
        if not hasattr(self,"_grid_img") or self._grid_img is None: return
        ix,iy=self._grid_canvas_to_img(event.x,event.y)
        col,row=self._pixel_to_grid(ix,iy)
        self.grid_info_lbl.config(text=f"Pixel: ({int(ix)},{int(iy)})  →  Case: ({col},{row})")

    def _grid_canvas_to_img(self,cx,cy):
        if not hasattr(self,"_grid_scale"): return cx,cy
        scale=self._grid_scale
        ox=getattr(self,"_grid_draw_ox",0); oy=getattr(self,"_grid_draw_oy",0)
        if scale==0: return cx,cy
        return (cx-ox)/scale,(cy-oy)/scale

    def _grid_canvas_redraw(self,event=None):
        canvas=self.grid_canvas
        canvas.delete("all")
        cw=canvas.winfo_width(); ch=canvas.winfo_height()
        if cw<10 or ch<10: return
        if not hasattr(self,"_grid_img") or self._grid_img is None:
            canvas.create_text(cw//2,ch//2,
                text="📸 Cliquez 'Capturer' pour charger la vue",
                fill=C["sub"],font=("Segoe UI",12)); return
        img=self._grid_img.copy(); iw,ih=img.size
        scale=min(cw/iw,ch/ih); nw,nh=int(iw*scale),int(ih*scale)
        self._grid_scale=scale
        self._grid_draw_ox=(cw-nw)//2; self._grid_draw_oy=(ch-nh)//2
        draw=ImageDraw.Draw(img)
        if self.template_cache and self.grid_show_detect_var.get():
            ss_cv=pil_to_cv(self._grid_img)
            threshold=self.thresh_var.get() if hasattr(self,"thresh_var") else 0.75
            type_colors={
                "Grille : Case vide":           ("#33cc33","#33cc3360"),
                "Grille : Case obstacle":       ("#cc3333","#cc333380"),
                "Grille : Case mur":            ("#888888","#666666aa"),
                "Grille : Bord de map":         ("#555555","#444444aa"),
                "Grille : Case survolée":       ("#cccc00","#cccc0060"),
                "Grille : Case occupée joueur": ("#22cc66","#22cc66cc"),
                "Grille : Case occupée allié":  ("#4488ff","#4488ffcc"),
                "Grille : Case occupée ennemi": ("#ff4444","#ff4444cc"),
                "Grille : Case occupée monstre":("#ff8800","#ff8800cc"),
            }
            for tid,meta in self.config.get("templates",{}).items():
                ttype=meta.get("type","")
                cv_list=self.template_cache.get(tid,[])
                if not cv_list: continue
                matches=find_template_multi(ss_cv,cv_list,threshold)
                if not matches: continue
                outline_c,_=type_colors.get(ttype,("#ffffff","#ffffff40"))
                for m in matches:
                    x,y,tw,th,conf=m
                    draw.rectangle([x,y,x+tw,y+th],outline=outline_c,width=2)
                    label=f"{meta.get('name','?')} {conf:.0%}"
                    try:
                        bbox=draw.textbbox((x,y-14),label)
                        draw.rectangle([bbox[0]-1,bbox[1]-1,bbox[2]+1,bbox[3]+1],fill=outline_c)
                        draw.text((x,y-14),label,fill="white")
                    except: draw.text((x,y-14),label,fill=outline_c)
        resized=img.resize((nw,nh),Image.LANCZOS)
        self._grid_photo=ImageTk.PhotoImage(resized)
        canvas.create_image(self._grid_draw_ox,self._grid_draw_oy,
                            anchor="nw",image=self._grid_photo)

    # ══════════════════════════════════════════════════════
    # SCAN
    # ══════════════════════════════════════════════════════
    def _on_thresh_changed(self,val):
        self.config["confidence_threshold"]=self.thresh_var.get()

    def _toggle_scan(self):
        if self.scanning:
            self.scanning=False
            self.scan_btn.config(text="▶ Démarrer la séquence (F8)",bg=C["green"])
            self._log("Séquences arrêtées — le preview continue")
        else:
            if not self.selected_hwnd or not win32gui.IsWindow(self.selected_hwnd):
                self._log("Fenêtre invalide","error"); return
            if not self.template_cache:
                self._log("Aucun template chargé","error"); return
            self.scanning=True; self.paused=False
            self.config["scan_interval_ms"]=self.interval_var.get()
            self.scan_btn.config(text="⏹ Arrêter la séquence (F8)",bg=C["red"])
            total=sum(len(v) for v in self.template_cache.values())
            self._log(f"Séquences démarrées — {len(self.template_cache)} templates ({total} imgs)","ok")

    def _start_live_preview(self):
        if hasattr(self,"_live_thread_running") and self._live_thread_running: return
        self._live_thread_running=True
        self._scan_frame_count=0; self._scan_det_count=0
        self.live_thread=threading.Thread(target=self._live_preview_loop,daemon=True)
        self.live_thread.start()
        self._log("Preview live démarré","ok")

    def _live_preview_loop(self):
        consecutive_errors=0; self._last_display_time=0
        while self._live_thread_running:
            try:
                if not self.selected_hwnd or not win32gui.IsWindow(self.selected_hwnd):
                    self.root.after(0,self._scan_show_no_signal); time.sleep(1); continue
                ss=capture_window(self.selected_hwnd)
                if ss is None:
                    consecutive_errors+=1
                    if consecutive_errors>10: consecutive_errors=0
                    self.root.after(0,self._scan_show_no_signal); time.sleep(0.5); continue
                consecutive_errors=0
                self._scan_frame_count+=1
                ss_cv=pil_to_cv(ss)
                threshold=self.thresh_var.get()
                ox=self.config.get("calibration_offset_x",0)
                oy=self.config.get("calibration_offset_y",0)
                try: scr_x,scr_y=win32gui.ClientToScreen(self.selected_hwnd,(0,0))
                except: scr_x,scr_y=0,0
                det_map={}
                if self.template_cache:
                    for tid,cv_list in self.template_cache.items():
                        if not cv_list: continue
                        matches=find_template_multi(ss_cv,cv_list,threshold)
                        if matches: det_map[tid]=matches
                self._scan_det_count=sum(len(m) for m in det_map.values())
                display_img=ss.copy(); draw=ImageDraw.Draw(display_img)
                det_lines=[]
                colors_list=["#ff4444","#44ff44","#4488ff","#ff44ff",
                             "#ffaa00","#00ffff","#ff8800","#88ff00"]
                color_idx=0
                for tid,matches in det_map.items():
                    meta=self.config["templates"].get(tid,{})
                    col=colors_list[color_idx%len(colors_list)]; color_idx+=1
                    for m in matches:
                        x,y,tw,th,conf=m
                        draw.rectangle([x,y,x+tw,y+th],outline=col,width=2)
                        bar_w=int(tw*conf)
                        draw.rectangle([x,y-4,x+bar_w,y-1],fill=col)
                        draw.rectangle([x,y-4,x+tw,y-1],outline=col)
                        label=f"{meta.get('name','?')} {conf:.0%}"
                        try:
                            bbox=draw.textbbox((x,y-18),label)
                            draw.rectangle([bbox[0]-1,bbox[1]-1,bbox[2]+1,bbox[3]+1],fill=col)
                            draw.text((x,y-18),label,fill="white")
                        except: draw.text((x,y-18),label,fill=col)
                        tag="high" if conf>=0.85 else "medium" if conf>=0.70 else "low"
                        n_var=meta.get("variant_count",1)
                        det_lines.append(
                            (f"  {meta.get('name','?')} [{meta.get('category','')}] "
                             f"@ ({x},{y}) conf={conf:.1%} ({n_var}v)", tag))
                _now=time.time()
                if _now-self._last_display_time>0.033:
                    self._last_display_time=_now
                    self.root.after(0,self._scan_update_display,display_img,det_lines)
                if self.scanning and not self.paused:
                    self._execute_all_sequences(det_map,ss_cv,scr_x,scr_y,ox,oy,threshold)
                interval=self.interval_var.get()
                time.sleep(max(interval,80)/1000.0)
            except Exception as e:
                consecutive_errors+=1
                err_msg=str(e)
                if err_msg!=getattr(self,"_scan_last_error",""):
                    self._scan_last_error=err_msg
                    self.root.after(0,lambda m=err_msg: self._log(f"Preview : {m}","error"))
                time.sleep(1)

    def _toggle_pause(self):
        self.paused=not self.paused
        self.root.after(0,lambda: self.pause_lbl.config(
            text="⏸ PAUSE" if self.paused else ""))

    def _scan_show_no_signal(self):
        self.scan_canvas.delete("all")
        cw=self.scan_canvas.winfo_width(); ch=self.scan_canvas.winfo_height()
        self.scan_canvas.create_text(cw//2,ch//2,
            text="⚠ Pas de signal — capture échouée",
            fill=C["yellow"],font=("Segoe UI",14))
        self.scan_stats_lbl.config(
            text=f"Frames: {self._scan_frame_count} | Détections: 0 | ⚠ Erreur capture")

    def _scan_update_display(self,pil_img,det_lines):
        cw=self.scan_canvas.winfo_width(); ch=self.scan_canvas.winfo_height()
        if cw<10 or ch<10: return
        iw,ih=pil_img.size; scale=min(cw/iw,ch/ih)
        nw=int(iw*scale); nh=int(ih*scale)
        resized=pil_img.resize((nw,nh),Image.NEAREST)
        self._scan_photo=ImageTk.PhotoImage(resized)
        self.scan_canvas.delete("all")
        ox=(cw-nw)//2; oy=(ch-nh)//2
        self.scan_canvas.create_image(ox,oy,anchor="nw",image=self._scan_photo)
        self.scan_stats_lbl.config(
            text=f"Frame #{self._scan_frame_count} | "
                 f"{self._scan_det_count} détection(s) | "
                 f"Seuil: {self.thresh_var.get():.0%}")
        self.scan_det_text.config(state="normal")
        self.scan_det_text.delete("1.0","end")
        if det_lines:
            for text,tag in det_lines: self.scan_det_text.insert("end",text+"\n",tag)
        else:
            self.scan_det_text.insert("end","  (aucune détection)")
        self.scan_det_text.config(state="disabled")

    def _execute_all_sequences(self,det_map,ss_cv,scr_x,scr_y,ox,oy,threshold):
        def run_seq(seq,depth=0):
            if not seq.get("enabled",True): return
            if not self.scanning or self.paused: return
            indent="  "*depth
            if not self._check_conditions(seq,det_map):
                cond_names=[]
                for c in seq.get("conditions",[]):
                    m=self.config["templates"].get(c.get("template",""),{})
                    mode="absent" if c.get("mode")=="absent" else "présent"
                    detected=c.get("template","") in det_map and len(det_map.get(c.get("template",""),[])) > 0
                    status="détecté" if detected else "absent"
                    cond_names.append(f"{m.get('name','?')}({mode}→{status})")
                reason=", ".join(cond_names)
                self.root.after(0,lambda n=seq["name"],d=indent,r=reason:
                    self._log(f"{d}⏭ Conditions non remplies: {n} [{r}]","info")); return
            self.root.after(0,lambda n=seq["name"],d=indent:
                self._log(f"{d}▶ Exécution: {n}","info"))
            result=self._execute_sequence_steps(seq,det_map,ss_cv,scr_x,scr_y,ox,oy,threshold)
            if result:
                self.root.after(0,lambda n=seq["name"],d=indent:
                    self._log(f"{d}✓ Séquence OK: {n}","ok"))
            else:
                self.root.after(0,lambda n=seq["name"],d=indent:
                    self._log(f"{d}⏭ Séquence skip: {n}","info"))
            for child in seq.get("children",[]):
                if not self.scanning or self.paused: return
                run_seq(child,depth+1)
        for seq in self.config["sequences"]:
            if not self.scanning or self.paused: break
            run_seq(seq)

    def _execute_sequence_steps(self,seq,det_map,ss_cv,scr_x,scr_y,ox,oy,threshold):
        hover_ms=self.config.get("hover_delay_ms",150)
        action_ms=self.config.get("action_delay_ms",300)
        last_match=None; completed=True
        for step_idx,step in enumerate(seq.get("steps",[])):
            if not self.scanning or self.paused: completed=False; break
            stype=step.get("type",""); tpl_tid=step.get("template",""); val=step.get("value","")
            tpl_name=self.config["templates"].get(tpl_tid,{}).get("name","?") if tpl_tid else ""
            if stype=="detect":
                if tpl_tid in det_map and det_map[tpl_tid]:
                    last_match=det_map[tpl_tid][0]
                    self.root.after(0,lambda i=step_idx,n=tpl_name,c=last_match[4]:
                        self._log(f"  étape {i+1}: detect '{n}' → trouvé ({c:.0%})","ok"))
                else:
                    self.root.after(0,lambda i=step_idx,n=tpl_name:
                        self._log(f"  étape {i+1}: detect '{n}' → absent","warn"))
                    completed=False; break
            elif stype=="hover":
                if last_match:
                    cx=scr_x+last_match[0]+last_match[2]//2+ox
                    cy=scr_y+last_match[1]+last_match[3]//2+oy
                    win32api.SetCursorPos((cx,cy))
                    self.root.after(0,lambda i=step_idx,x=cx,y=cy:
                        self._log(f"  étape {i+1}: hover → ({x},{y})","ok"))
                    time.sleep(hover_ms/1000.0)
            elif stype in ("click_gauche","click_droit"):
                if last_match:
                    cx=scr_x+last_match[0]+last_match[2]//2+ox
                    cy=scr_y+last_match[1]+last_match[3]//2+oy
                    win32api.SetCursorPos((cx,cy)); time.sleep(0.05)
                    if stype=="click_gauche":
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,cx,cy,0,0)
                        time.sleep(0.02)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,cx,cy,0,0)
                    else:
                        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,cx,cy,0,0)
                        time.sleep(0.02)
                        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,cx,cy,0,0)
                    self.root.after(0,lambda i=step_idx,s=stype,x=cx,y=cy:
                        self._log(f"  étape {i+1}: {s} → ({x},{y})","ok"))
                    time.sleep(action_ms/1000.0)
            elif stype=="wait":
                try: ms=int(val) if val else action_ms
                except: ms=action_ms
                time.sleep(ms/1000.0)
            elif stype in ("detect_then_click","detect_then_rclick"):
                time.sleep(0.15)
                ss2=capture_window(self.selected_hwnd)
                if ss2 is None: completed=False; break
                cv_list=self.template_cache.get(tpl_tid,[])
                if not cv_list: completed=False; break
                matches=find_template_multi(pil_to_cv(ss2),cv_list,threshold)
                if matches:
                    m=matches[0]
                    cx=scr_x+m[0]+m[2]//2+ox; cy=scr_y+m[1]+m[3]//2+oy
                    win32api.SetCursorPos((cx,cy)); time.sleep(hover_ms/1000.0)
                    if stype=="detect_then_click":
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,cx,cy,0,0)
                        time.sleep(0.02)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,cx,cy,0,0)
                    else:
                        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,cx,cy,0,0)
                        time.sleep(0.02)
                        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,cx,cy,0,0)
                    last_match=m
                    self.root.after(0,lambda i=step_idx,n=tpl_name,c=m[4],x=cx,y=cy:
                        self._log(f"  étape {i+1}: click sur '{n}' ({c:.0%}) → ({x},{y})","ok"))
                    time.sleep(action_ms/1000.0)
                else: completed=False; break
            elif stype=="touche":
                try: keyboard.press_and_release(val if val else "&")
                except: pass
                time.sleep(0.1)
            elif stype=="combo_touches":
                if val:
                    try:
                        keyboard.press_and_release(val)
                        self.root.after(0,lambda i=step_idx,k=val:
                            self._log(f"  étape {i+1}: combo '{k}'","ok"))
                    except Exception as ke:
                        self.root.after(0,lambda i=step_idx,e=str(ke):
                            self._log(f"  étape {i+1}: combo erreur: {e}","error"))
                time.sleep(0.1)
            elif stype=="bind_slot":
                slot=val.strip() if val else "1"
                key=SLOT_KEYS.get(slot,slot)
                try:
                    keyboard.press_and_release(key)
                    self.root.after(0,lambda i=step_idx,s=slot,k=key:
                        self._log(f"  étape {i+1}: slot {s} ('{k}')","ok"))
                except: pass
                time.sleep(0.15)
            elif stype=="clic_position":
                try:
                    parts=val.replace(" ","").split(",")
                    px,py=int(parts[0]),int(parts[1])
                    cx=scr_x+px+ox; cy=scr_y+py+oy
                    win32api.SetCursorPos((cx,cy)); time.sleep(0.05)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,cx,cy,0,0)
                    time.sleep(0.02)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,cx,cy,0,0)
                    self.root.after(0,lambda i=step_idx,x=cx,y=cy:
                        self._log(f"  étape {i+1}: clic fixe → ({x},{y})","ok"))
                except Exception as pe:
                    self.root.after(0,lambda i=step_idx,e=str(pe):
                        self._log(f"  étape {i+1}: clic_position erreur: {e}","error"))
                time.sleep(action_ms/1000.0)
            elif stype=="clic_grille":
                try:
                    parts=val.replace(" ","").split(",")
                    col,row=int(parts[0]),int(parts[1])
                    gpx,gpy=self._grid_to_pixel(col,row)
                    cx=scr_x+gpx+ox; cy=scr_y+gpy+oy
                    win32api.SetCursorPos((cx,cy)); time.sleep(0.05)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,cx,cy,0,0)
                    time.sleep(0.02)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,cx,cy,0,0)
                    self.root.after(0,lambda i=step_idx,c=col,r=row,x=cx,y=cy:
                        self._log(f"  étape {i+1}: grille ({c},{r}) → ({x},{y})","ok"))
                except Exception as ge:
                    self.root.after(0,lambda i=step_idx,e=str(ge):
                        self._log(f"  étape {i+1}: clic_grille erreur: {e}","error"))
                time.sleep(action_ms/1000.0)
            elif stype=="pause_si_present":
                if tpl_tid in det_map and det_map[tpl_tid]:
                    self.paused=True
                    self.root.after(0,lambda: self.pause_lbl.config(text="⏸ PAUSE (auto)")); break
            elif stype=="sous_sequence":
                sub_id=step.get("sub_sequence_id")
                if sub_id:
                    sub_seq=self._get_seq_by_id(sub_id)
                    if sub_seq:
                        self._execute_sequence_steps(sub_seq,det_map,ss_cv,scr_x,scr_y,ox,oy,threshold)
            elif stype=="si_detecte_alors":
                sub_id=step.get("sub_sequence_id")
                if tpl_tid in det_map and det_map[tpl_tid] and sub_id:
                    sub_seq=self._get_seq_by_id(sub_id)
                    if sub_seq:
                        self.root.after(0,lambda n=tpl_name,sn=sub_seq["name"]:
                            self._log(f"  → '{n}' détecté, lancement '{sn}'","ok"))
                        self._execute_sequence_steps(sub_seq,det_map,ss_cv,scr_x,scr_y,ox,oy,threshold)
            elif stype=="si_absent_alors":
                sub_id=step.get("sub_sequence_id")
                if not (tpl_tid in det_map and len(det_map.get(tpl_tid,[]))>0) and sub_id:
                    sub_seq=self._get_seq_by_id(sub_id)
                    if sub_seq:
                        self.root.after(0,lambda n=tpl_name,sn=sub_seq["name"]:
                            self._log(f"  → '{n}' absent, lancement '{sn}'","ok"))
                        self._execute_sequence_steps(sub_seq,det_map,ss_cv,scr_x,scr_y,ox,oy,threshold)
            elif stype in ("attendre_detection","attendre_disparition"):
                timeout=10000
                try: timeout=int(val) if val else 10000
                except: pass
                start=time.time(); found_state=False
                cv_list=self.template_cache.get(tpl_tid,[])
                while time.time()-start < timeout/1000.0:
                    if not self.scanning or self.paused: break
                    ss_tmp=capture_window(self.selected_hwnd)
                    if ss_tmp:
                        matches=find_template_multi(pil_to_cv(ss_tmp),cv_list,threshold)
                        if stype=="attendre_detection" and matches:
                            last_match=matches[0]; found_state=True; break
                        elif stype=="attendre_disparition" and not matches:
                            found_state=True; break
                    time.sleep(0.2)
                action_word="apparu" if stype=="attendre_detection" else "disparu"
                if found_state:
                    self.root.after(0,lambda i=step_idx,n=tpl_name,aw=action_word:
                        self._log(f"  étape {i+1}: '{n}' {aw} ✓","ok"))
                else:
                    self.root.after(0,lambda i=step_idx,n=tpl_name:
                        self._log(f"  étape {i+1}: timeout '{n}'","warn"))
                    completed=False; break
            time.sleep(0.03)
        return completed

    # ══════════════════════════════════════════════════════
    # HOTKEYS & LOG
    # ══════════════════════════════════════════════════════
    def _setup_hotkeys(self):
        try:
            keyboard.on_press_key("F5",  lambda _: self.root.after(0,self._grab_clipboard))
            keyboard.on_press_key("F8",  lambda _: self.root.after(0,self._toggle_scan))
            keyboard.on_press_key("F9",  lambda _: self.root.after(0,self._toggle_pause))
            keyboard.on_press_key("F10", lambda _: self.root.after(0,self._on_close))
            self._log("Hotkeys : F5=Coller  F8=Scan  F9=Pause  F10=Quitter","ok")
        except Exception as e:
            self._log(f"Hotkeys : {e}","warn")

    def _log(self,msg,level="info"):
        ts=datetime.now().strftime("%H:%M:%S")
        prefix={"info":"·","ok":"✓","warn":"⚠","error":"✗"}.get(level,"·")
        line=f"[{ts}] {prefix} {msg}\n"
        self.log_text.configure(state="normal")
        self.log_text.insert("end",line,level)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0","end")
        self.log_text.configure(state="disabled")

    def _copy_log(self):
        try:
            content=self.log_text.get("1.0","end")
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self._log("Log copié ✓","ok")
        except: pass

    # ══════════════════════════════════════════════════════
    # CLOSE
    # ══════════════════════════════════════════════════════
    def _on_close(self):
        self.scanning=False
        self.config["confidence_threshold"]=self.thresh_var.get()
        self.config["scan_interval_ms"]=self.interval_var.get()
        save_config(self.config)
        try: keyboard.unhook_all()
        except: pass
        self.root.destroy()

    def run(self):
        self._start_live_preview()
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = WakfuVisionApp()
        app.run()
    except Exception:
        err=traceback.format_exc()
        ts=datetime.now().strftime("%Y%m%d_%H%M%S")
        msg=f"[ERREUR Vision Automator v4.0 — {ts}]\n{err}"
        print(msg)
        try:
            p=subprocess.Popen(["clip.exe"],stdin=subprocess.PIPE)
            p.communicate(msg.encode("utf-8"))
        except: pass
        input("Appuyez sur Entrée pour fermer...")









