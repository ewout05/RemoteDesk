from flask import Flask, render_template, request, abort
import pyautogui
import keyboard
import threading
import pythoncom
import queue
import socket
import qrcode_terminal
import tkinter as tk

from pycaw.pycaw import IAudioEndpointVolume
from pycaw.utils import AudioUtilities
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

app = Flask(__name__)

pyautogui.FAILSAFE = True

touch_state = {"active": False}
touch_lock = threading.Lock()
volume_queue = queue.Queue()


# -----------------------------
# AUDIO / VOLUME
# -----------------------------

def get_volume_status():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    )
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    muted = volume.GetMute()
    percent = int(volume.GetMasterVolumeLevelScalar() * 100)
    return muted, percent


def volume_overlay_thread():
    pythoncom.CoInitialize()
    try:
        muted, percent = get_volume_status()
        if muted:
            volume_queue.put("🔇 Mute")
        else:
            volume_queue.put(f"🔊 Volume: {percent}%")
    finally:
        pythoncom.CoUninitialize()


# -----------------------------
# TK OVERLAY
# -----------------------------

def start_overlay_window():
    root = tk.Tk()
    root.withdraw()

    overlay = tk.Toplevel(root)
    overlay.withdraw()
    overlay.overrideredirect(True)
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", 0.85)
    overlay.configure(bg="black")
    overlay.geometry("+20+20")

    label = tk.Label(
        overlay,
        text="",
        font=("Segoe UI", 24),
        fg="white",
        bg="black"
    )
    label.pack(padx=20, pady=10)

    overlay_state = {"timer": None, "shown": False}

    def refresh():
        try:
            message = volume_queue.get_nowait()
            label.config(text=message)

            if not overlay_state["shown"]:
                overlay.deiconify()
                overlay_state["shown"] = True

            if overlay_state["timer"]:
                root.after_cancel(overlay_state["timer"])

            overlay_state["timer"] = root.after(
                2000,
                lambda: (
                    overlay.withdraw(),
                    overlay_state.update({"shown": False})
                )
            )

        except queue.Empty:
            pass

        root.after(100, refresh)

    refresh()
    root.mainloop()


# -----------------------------
# FLASK ROUTES
# -----------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/touch_start", methods=["POST"])
def touch_start():
    with touch_lock:
        touch_state["active"] = True
    return "OK"


@app.route("/touch_end", methods=["POST"])
def touch_end():
    with touch_lock:
        touch_state["active"] = False
    return "OK"


@app.route("/move_relative", methods=["POST"])
def move_relative():
    with touch_lock:
        if not touch_state["active"]:
            abort(403)

    dx = float(request.form.get("dx", 0))
    dy = float(request.form.get("dy", 0))

    x, y = pyautogui.position()
    screen_w, screen_h = pyautogui.size()

    scale = 3
    margin = 5

    new_x = max(margin, min(screen_w - margin, x + dx * scale))
    new_y = max(margin, min(screen_h - margin, y + dy * scale))

    pyautogui.moveTo(new_x, new_y)
    return "OK"


@app.route("/click", methods=["POST"])
def click():
    button = request.form.get("button", "left")
    double = request.form.get("double") == "true"

    if double:
        pyautogui.click(button=button, clicks=2, interval=0.15)
    else:
        pyautogui.click(button=button)

    return "OK"


@app.route("/key", methods=["POST"])
def key():
    key_name = request.form.get("key")
    if not key_name:
        abort(400)

    keyboard.send(key_name)
    return "OK"


@app.route("/media", methods=["POST"])
def media():
    action = request.form.get("action")

    if action == "volume_up":
        keyboard.send("volume up")
        threading.Thread(target=volume_overlay_thread, daemon=True).start()

    elif action == "volume_down":
        keyboard.send("volume down")
        threading.Thread(target=volume_overlay_thread, daemon=True).start()

    elif action == "mute":
        keyboard.send("volume mute")
        threading.Thread(target=volume_overlay_thread, daemon=True).start()

    elif action == "play_pause":
        keyboard.send("play/pause media")

    elif action == "fullscreen_browser":
        keyboard.send("f11")

    elif action == "fullscreen_video":
        keyboard.send("f")

    else:
        abort(400)

    return "OK"


# -----------------------------
# IP DETECTIE + SERVER START
# -----------------------------

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def run_flask():
    ip = get_local_ip()
    url = f"http://{ip}:5000"
    print(f"Open op je telefoon: {url}")
    qrcode_terminal.draw(url, )
    app.run(host="0.0.0.0", port=5000, debug=False)


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    start_overlay_window()