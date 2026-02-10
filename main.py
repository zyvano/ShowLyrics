import sys
import os
import webbrowser
import threading
import time
import json
import uvicorn
import uuid
import re

# --- FIX IMPORT DI SINI ---
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse # <--- INI YG TADI HILANG
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pythonosc import udp_client

# --- CONFIGURATION (SAMA KAYAK SEBELUMNYA) ---

# 1. Fungsi cari aset (HTML/Logo) -> Tetap di dalam EXE
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 2. Fungsi cari Database -> PINDAH KE DOCUMENTS USER
def get_user_data_path(filename):
    user_docs = os.path.expanduser("~/Documents")
    app_folder = os.path.join(user_docs, "WorshipEngineData")
    if not os.path.exists(app_folder):
        os.makedirs(app_folder)
    return os.path.join(app_folder, filename)

# --- INIT APP ---
app = FastAPI()

# Mount Static & Templates
app.mount("/static", StaticFiles(directory=get_resource_path("static")), name="static")
templates = Jinja2Templates(directory=get_resource_path("templates"))

# Database path
SONGS_FILE = get_user_data_path("songs.json")
SERVICE_FILE = get_user_data_path("service.json")
SCHEDULES_FILE = get_user_data_path("schedules.json")
LT_PRESETS_FILE = get_user_data_path("lt_presets.json")
DISPLAY_PRESETS_FILE = get_user_data_path("display_presets.json")
FB_PRESETS_FILE = get_user_data_path("fb_presets.json")

# ... (di dalam loop for fpath...)
for fpath in [SONGS_FILE, SERVICE_FILE, SCHEDULES_FILE, LT_PRESETS_FILE, DISPLAY_PRESETS_FILE, FB_PRESETS_FILE]: # <-- Tambah FB
    if not os.path.exists(fpath):
        with open(fpath, "w") as f:
            if fpath in [SCHEDULES_FILE, LT_PRESETS_FILE, DISPLAY_PRESETS_FILE, FB_PRESETS_FILE]: 
                json.dump({}, f)
            else: 
                json.dump([], f)

osc_client = udp_client.SimpleUDPClient("127.0.0.1", 7000)

def load_json(path):
    try:
        with open(path, "r") as f: return json.load(f)
    except: return {}

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=4)


# ... (SISA KODE KE BAWAH GA PERLU DIUBAH) ...

# --- MODELS (Sama kayak sebelumnya) ---
class Song(BaseModel):
    title: str
    data: List[Dict[str, Any]]
    settings: Optional[Dict[str, Any]] = {}

class SavedSchedule(BaseModel):
    name: str
    items: List[str]

# --- CONNECTION MANAGER ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        
        # 1. State Default (Hardcoded fallback)
        self.current_state = { 
            "text": "", "font": "Cinzel", "color": "#ffffff", "zoom": "in", 
            "speed": "30s", "glow": 50, "fade": 0.5, "show": False,
            "theme": "default", "trans": "fade", "next_text": ""
        }
        self.lt_state = {}
        self.fb_state = {}

        # 2. LANGSUNG LOAD DARI FILE SAAT INIT (FIX BUG DISPLAY)
        self.load_all_defaults()

    def load_all_defaults(self):
        print("[INIT] Loading Presets from Disk...")
        
        # Load Main Display Default
        try:
            disp_data = load_json(DISPLAY_PRESETS_FILE)
            def_name = disp_data.get("default")
            if def_name and def_name in disp_data.get("presets", {}):
                print(f" -> Display Default Loaded: {def_name}")
                # Update current_state tapi jangan timpa text/show status
                preset = disp_data["presets"][def_name]
                for k, v in preset.items():
                    self.current_state[k] = v
        except Exception as e: print(f"Error loading Display default: {e}")

        # Load Lower Third Default
        try:
            lt_data = load_json(LT_PRESETS_FILE)
            def_name = lt_data.get("default")
            if def_name and def_name in lt_data.get("presets", {}):
                print(f" -> LT Default Loaded: {def_name}")
                self.lt_state = lt_data["presets"][def_name]
        except Exception as e: print(f"Error loading LT default: {e}")

        # Load Foldback Default
        try:
            fb_data = load_json(FB_PRESETS_FILE)
            def_name = fb_data.get("default")
            if def_name and def_name in fb_data.get("presets", {}):
                print(f" -> FB Default Loaded: {def_name}")
                self.fb_state = fb_data["presets"][def_name]
        except Exception as e: print(f"Error loading FB default: {e}")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Kirim SEMUA State yang sudah ter-load ke Client baru
        await websocket.send_json({"type": "update_state", "state": self.current_state})
        
        if self.lt_state:
            await websocket.send_json({"type": "update_lt_config", "config": self.lt_state})
            
        if self.fb_state:
            await websocket.send_json({"type": "update_fb_config", "config": self.fb_state})

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections: self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections: await connection.send_json(data)


manager = ConnectionManager()

# --- ROUTES HTML ---
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/display", response_class=HTMLResponse)
async def get_display(request: Request):
    return templates.TemplateResponse("display.html", {"request": request})

@app.get("/control", response_class=HTMLResponse)
async def get_control(request: Request):
    return templates.TemplateResponse("control.html", {"request": request})

# NEW ROUTE: RESOLUME CONTROLLER
@app.get("/resolume", response_class=HTMLResponse)
async def get_resolume(request: Request):
    return templates.TemplateResponse("resolume.html", {"request": request})

# --- NEW ROUTE: LOWER THIRD ---
@app.get("/lowerthird", response_class=HTMLResponse)
async def get_lowerthird(request: Request):
    return templates.TemplateResponse("lowerthird.html", {"request": request})

# --- NEW ROUTE: FOLDBACK (STAGE DISPLAY) ---
@app.get("/foldback", response_class=HTMLResponse)
async def get_foldback(request: Request):
    return templates.TemplateResponse("foldback.html", {"request": request})

# --- HELPER & API (Sama persis kayak sebelumnya - Copy Paste yg lama gpp) ---
# ... (Bagian API Songs, Service, Import TXT tetep sama, gw singkat biar hemat space) ...
# Copy paste fungsi load_json, save_json, dan semua route @app.get/post/delete API disini
# PASTIKAN SEMUA API LAMA ADA DISINI (gw assume lu copy full dari main.py sebelumnya)

@app.get("/api/songs")
async def get_songs(): return load_json(SONGS_FILE)

@app.post("/api/songs")
async def save_song(song: Song):
    songs = load_json(SONGS_FILE)
    existing_index = next((index for (index, d) in enumerate(songs) if d["title"] == song.title), None)
    if existing_index is not None: songs[existing_index] = song.dict()
    else: songs.append(song.dict())
    save_json(SONGS_FILE, songs)
    return {"status": "success"}

@app.delete("/api/songs/{title}")
async def delete_song(title: str):
    songs = load_json(SONGS_FILE)
    songs = [s for s in songs if s["title"] != title]
    save_json(SONGS_FILE, songs)
    return {"status": "success"}

@app.get("/api/service")
async def get_service(): return load_json(SERVICE_FILE)

@app.post("/api/service")
async def save_service(items: List[str]):
    save_json(SERVICE_FILE, items)
    return {"status": "success"}

@app.get("/api/schedules")
async def get_schedules(): return load_json(SCHEDULES_FILE)

@app.post("/api/schedules")
async def save_schedule_named(sched: SavedSchedule):
    data = load_json(SCHEDULES_FILE)
    data[sched.name] = sched.items
    save_json(SCHEDULES_FILE, data)
    return {"status": "success"}

@app.delete("/api/schedules/{name}")
async def delete_schedule_named(name: str):
    data = load_json(SCHEDULES_FILE)
    if name in data: del data[name]
    save_json(SCHEDULES_FILE, data)
    return {"status": "success"}

@app.post("/import_songs")
async def import_songs(files: List[UploadFile] = File(...)):
    new_songs = []
    current_songs = load_json(SONGS_FILE)
    count_success = 0

    for file in files:
        if file.filename.endswith(".txt"):
            try:
                content = await file.read()
                try: text = content.decode("utf-8")
                except: text = content.decode("latin-1", errors="ignore")
                
                # Normalisasi Enter
                text = text.replace("\r\n", "\n").replace("\r", "\n")
                
                # Split Slide (2x Enter atau lebih = Slide Baru)
                raw_slides = re.split(r'\n\s*\n', text)
                
                final_slides = []
                for s in raw_slides:
                    clean_s = s.strip()
                    if clean_s: final_slides.append(clean_s)
                
                if final_slides:
                    title = os.path.splitext(file.filename)[0]
                    # Format data sesuai schema Song
                    song_obj = {
                        "title": title,
                        "data": [{"id": i, "text": txt, "type": "normal"} for i, txt in enumerate(final_slides)],
                        "settings": {}
                    }
                    new_songs.append(song_obj)
                    count_success += 1
            except Exception as e:
                print(f"Error {file.filename}: {e}")

    # Gabung Data
    if new_songs:
        # Hapus lagu lama kalau namanya sama (replace logic)
        existing_titles = [s["title"] for s in new_songs]
        current_songs = [s for s in current_songs if s["title"] not in existing_titles]
        current_songs.extend(new_songs)
        save_json(SONGS_FILE, current_songs)
            
    return {"status": "success", "count": count_success}

    # --- LOWER THIRD PRESET APIs ---

@app.get("/api/lt_presets")
async def get_lt_presets():
    return load_json(LT_PRESETS_FILE)

@app.post("/api/lt_presets")
async def save_lt_preset(payload: Dict[str, Any]):
    # Payload format: { "name": "NamaPreset", "config": {...}, "is_default": boolean }
    data = load_json(LT_PRESETS_FILE)
    
    # Init structure kalau file baru
    if "presets" not in data: data["presets"] = {}
    if "default" not in data: data["default"] = ""

    name = payload.get("name")
    config = payload.get("config")
    
    # Save preset
    data["presets"][name] = config
    
    # Set default kalau diminta
    if payload.get("is_default"):
        data["default"] = name
        
    save_json(LT_PRESETS_FILE, data)
    return {"status": "success"}

@app.post("/api/lt_presets/default/{name}")
async def set_default_lt_preset(name: str):
    data = load_json(LT_PRESETS_FILE)
    if "presets" in data and name in data["presets"]:
        data["default"] = name
        save_json(LT_PRESETS_FILE, data)
        return {"status": "success"}
    return {"status": "not_found"}

@app.delete("/api/lt_presets/{name}")
async def delete_lt_preset(name: str):
    data = load_json(LT_PRESETS_FILE)
    if "presets" in data and name in data["presets"]:
        del data["presets"][name]
        # Kalau yg dihapus itu default, reset defaultnya
        if data.get("default") == name:
            data["default"] = ""
        save_json(LT_PRESETS_FILE, data)
        return {"status": "success"}
    return {"status": "not_found"}
@app.get("/api/display_presets")
async def get_display_presets(): return load_json(DISPLAY_PRESETS_FILE)

@app.post("/api/display_presets")
async def save_display_preset(payload: Dict[str, Any]):
    data = load_json(DISPLAY_PRESETS_FILE)
    if "presets" not in data: data["presets"] = {}
    data["presets"][payload.get("name")] = payload.get("config")
    if payload.get("is_default"): data["default"] = payload.get("name")
    save_json(DISPLAY_PRESETS_FILE, data)
    return {"status": "success"}

@app.post("/api/display_presets/default/{name}")
async def set_default_display_preset(name: str):
    data = load_json(DISPLAY_PRESETS_FILE)
    if "presets" in data and name in data["presets"]:
        data["default"] = name
        save_json(DISPLAY_PRESETS_FILE, data)
        return {"status": "success"}
    return {"status": "not_found"}

@app.delete("/api/display_presets/{name}")
async def delete_display_preset(name: str):
    data = load_json(DISPLAY_PRESETS_FILE)
    if "presets" in data and name in data["presets"]:
        del data["presets"][name]
        if data.get("default") == name: data["default"] = ""
        save_json(DISPLAY_PRESETS_FILE, data)
        return {"status": "success"}
    return {"status": "not_found"}

    # --- FOLDBACK PRESET APIs ---

@app.get("/api/fb_presets")
async def get_fb_presets():
    return load_json(FB_PRESETS_FILE)

@app.post("/api/fb_presets")
async def save_fb_preset(payload: Dict[str, Any]):
    data = load_json(FB_PRESETS_FILE)
    if "presets" not in data: data["presets"] = {}
    
    data["presets"][payload.get("name")] = payload.get("config")
    
    if payload.get("is_default"):
        data["default"] = payload.get("name")
        
    save_json(FB_PRESETS_FILE, data)
    return {"status": "success"}

@app.post("/api/fb_presets/default/{name}")
async def set_default_fb_preset(name: str):
    data = load_json(FB_PRESETS_FILE)
    if "presets" in data and name in data["presets"]:
        data["default"] = name
        save_json(FB_PRESETS_FILE, data)
        return {"status": "success"}
    return {"status": "not_found"}

@app.delete("/api/fb_presets/{name}")
async def delete_fb_preset(name: str):
    data = load_json(FB_PRESETS_FILE)
    if "presets" in data and name in data["presets"]:
        del data["presets"][name]
        if data.get("default") == name: data["default"] = ""
        save_json(FB_PRESETS_FILE, data)
        return {"status": "success"}
    return {"status": "not_found"}

# --- WEBSOCKET WITH OSC HANDLER ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "update_display":
                manager.current_state.update(data.get("payload", {}))
                await manager.broadcast({"type": "update_state", "state": manager.current_state})
            
            # ... (kode update_display yang lama) ...
            # --- NEW ACTION: LOWER THIRD CONFIG ---
            elif action == "update_lowerthird":
                payload = data.get("payload")
                if payload:
                    manager.lt_state = payload # <--- SIMPAN KE MEMORI SERVER
                    await manager.broadcast({"type": "update_lt_config", "config": manager.lt_state})
            # FITUR BARU: Handle OSC Trigger

            elif action == "update_foldback":
                payload = data.get("payload")
                if payload:
                    manager.fb_state = payload
                    await manager.broadcast({"type": "update_fb_config", "config": manager.fb_state})

            elif action == "send_osc":
                address = data.get("address")
                # Bisa handle argument value kalau perlu, default 1 (Trigger Clip)
                if address:
                    try:
                        osc_client.send_message(address, 1)
                        print(f"OSC Sent: {address}")
                    except Exception as e:
                        print(f"OSC Error: {e}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    # Auto open browser setelah 1.5 detik
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:8000")

    threading.Thread(target=open_browser).start()
    
    # Jalanin Server
    uvicorn.run(app, host="0.0.0.0", port=8000)