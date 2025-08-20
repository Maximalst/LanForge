import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

def start_server():
    print("Server started")  # Insert server start code here

def stop_server():
    confirm = messagebox.askyesno("Confirmation", "Do you really want to stop the server?")
    if confirm:
        print("Server stopped")
        subprocess.Popen(["python3", "app.py"])

def install_requirements():
    """Installiert requirements.txt"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installiert")
    except subprocess.CalledProcessError as e:
        print("❌ Fehler beim Installieren:", e)

root = tk.Tk()
root.title("LanForge Admin")
root.geometry("800x600")
start_btn = tk.Button(root, text="Start Server", command=start_server)
start_btn.pack(pady=20)

stop_btn = tk.Button(root, text="Stop Server", command=stop_server)
stop_btn.pack(pady=20)

# Menüleiste erstellen
menubar = tk.Menu(root)

# Menü "Aktionen"
actions_menu = tk.Menu(menubar, tearoff=0)
actions_menu.add_command(label="Requirements installieren", command=install_requirements)
actions_menu.add_command(label="Server starten", command=start_server)
actions_menu.add_separator()
actions_menu.add_command(label="Beenden", command=root.quit)

menubar.add_cascade(label="Aktionen", menu=actions_menu)

root.config(menu=menubar)

root.mainloop()
root.mainloop()
