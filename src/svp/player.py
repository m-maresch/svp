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


def open_with_mpv(filepath):
    subprocess.Popen(
        [
            "mpv",
            filepath,
            "--hwdec=auto",
            "--profile=fast",
            "--scale=bilinear",
            "--cscale=bilinear",
            "--dscale=bilinear",
            "--video-sync=audio",
            "--interpolation=no",
            "--framedrop=vo",
            "--no-keep-open",
            "--osc",
            "--input-default-bindings=yes",
            "--input-vo-keyboard=yes",
            "--fs",  # Fullscreen
            "--no-sub-visibility",
            "--panscan=1.0",
        ]
    )


def open_with_player(filepath):
    if sys.platform == "win32":
        os.startfile(filepath)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", filepath])
    else:
        subprocess.Popen(["xdg-open", filepath])
