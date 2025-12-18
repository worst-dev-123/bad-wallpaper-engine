import subprocess
import os
import sys
import cv2 as cv
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

def SetWallpaper(path):
    if not os.path.exists(path):
        print(f"File {path} does NOT exist.")
        return

    uri = f"file://{os.path.abspath(path)}"
    subprocess.run([
        "gsettings", "set",
        "org.gnome.desktop.background",
        "picture-uri",
        uri
    ], check=True)

    subprocess.run([
        "gsettings", "set",
        "org.gnome.desktop.background",
        "picture-uri-dark",
        uri
    ], check=True)

def ExtractFrames(video_path, folder):
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)

    vid = cv.VideoCapture(video_path)
    count = 0
    success, image = vid.read()
    while success:
        frame_file = folder_path / f"frame{count:05d}.jpg"
        cv.imwrite(str(frame_file), image)
        success, image = vid.read()
        count += 1

    vid.release()

def SetLiveWallpaper(video_path):
    folder = Path(video_path).with_suffix('')
    if not folder.exists() or len(list(folder.iterdir())) == 0:
        print("Extracting frames...")
        ExtractFrames(video_path, folder)

    frames = sorted(folder.glob("*.jpg"))
    if not frames:
        print("No frames found!")
        return

    vid = cv.VideoCapture(video_path)
    fps = vid.get(cv.CAP_PROP_FPS) or 24
    vid.release()

    print(f"Starting live wallpaper at ~{fps:.2f} FPS with {len(frames)} frames...")

    try:
        while True:
            for frame in frames:
                SetWallpaper(str(frame))
                time.sleep(1 / fps)
    except KeyboardInterrupt:
        print("Stopped live wallpaper.")

def detect_desktop():
    session = os.getenv("XDG_SESSION_DESKTOP", "").lower()
    return session

def selectFile():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select Wallpaper (Image / Video)",
        filetypes=[
            ("All supported", "*.png *.jpg *.jpeg *.mp4"),
            ("Images", "*.png *.jpg *.jpeg"),
            ("Videos", "*.mp4"),
            ("All files", "*.*"),
        ]
    )

    if not file_path:
        return

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".mp4":
        SetLiveWallpaper(file_path)
    else:
        SetWallpaper(file_path)

if __name__ == "__main__":
    if detect_desktop() != "gnome":
        print("NOT running GNOME. Quitting...")
        sys.exit(1)

    selectFile()