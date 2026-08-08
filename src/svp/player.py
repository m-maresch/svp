import os
import sys
import subprocess


def open_with_vlc(filepath):
    subprocess.Popen(
        [
            "/Applications/VLC.app/Contents/MacOS/VLC",
            "--fullscreen",
            "--play-and-exit",
            filepath,
        ]
    )


def open_with_quicktime(filepath):
    subprocess.Popen(["open", "-a", "QuickTime Player", filepath])


def open_with_player(filepath):
    if sys.platform == "win32":
        os.startfile(filepath)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", filepath])
    else:
        subprocess.Popen(["xdg-open", filepath])
