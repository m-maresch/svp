import os
import sys
import subprocess


def open_file_with_player(filepath):
    if sys.platform == "win32":
        os.startfile(filepath)
    elif sys.platform == "darwin":
        subprocess.Popen(
            [
                "/Applications/VLC.app/Contents/MacOS/VLC",
                "--fullscreen",
                "--play-and-exit",
                filepath,
            ]
        )
    else:
        subprocess.Popen(["xdg-open", filepath])
