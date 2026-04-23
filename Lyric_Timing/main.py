import tkinter as tk
import os
import sys

# Ensure Python can import from this directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model import LyricModel
from player import AudioPlayer
from controller import AppController

def main():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
    
    JSON_PATH = os.path.join(PROJECT_DIR, "assets", "lyrics.json")
    MP3_PATH = os.path.join(PROJECT_DIR, "assets", "songs.mp3")

    root = tk.Tk()
    root.title("Lyric Timing Editor (MVC)")
    root.geometry("900x700")

    model = LyricModel(JSON_PATH)
    player = AudioPlayer(MP3_PATH)
    
    app_controller = AppController(root, model, player)

    root.mainloop()

if __name__ == "__main__":
    main()
