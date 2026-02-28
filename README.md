# RemoteDesk
a remote for windows

---

**WinRemote** is a lightweight remote‑control system for Windows that turns any phone or tablet into a wireless touchpad, keyboard, and media controller. It runs entirely in the browser—no app installation required. Simply start the server, scan the QR code in your terminal, and control your PC instantly.

### Features
- Wireless **touchpad** with smooth relative mouse movement  
- **Left and right click** buttons  
- Full **keyboard input**, including Enter, Backspace, Tab, Space  
- **Arrow keys** and navigation keys (Home, End, Page Up/Down, Esc)  
- **Media controls**: play/pause, next/previous track, volume up/down, mute  
- **Volume overlay** on Windows using a transparent Tkinter popup  
- **QR code** in the terminal for quick connection  
- Works on **any device** with a browser (Android, iOS, Windows, Linux)

### Technology
- Flask web server  
- PyAutoGUI for mouse control  
- Keyboard library for key events  
- Pycaw for Windows audio control  
- Tkinter overlay for volume feedback  
- qrcode‑terminal for terminal QR codes  

### Usage
Start the server:

```bash
python app.py
```

Scan the QR code or open the displayed URL on your phone.  
Your device becomes a full remote control for your PC.

