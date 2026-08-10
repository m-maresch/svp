import logging

import mpv

from PySide6.QtGui import QOpenGLContext, QPainter, QPainterPath, QColor
from PySide6.QtCore import Signal
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from style import BG_COLOR


class MPVVideoWidget(QOpenGLWidget):
    frame_ready = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mpv_player = None
        self.mpv_ctx = None
        self.frame_ready.connect(
            self.update
        )  # Connect signal to Qt's internal redraw loop

    def _emit_frame_ready(self):
        try:
            self.frame_ready.emit()
        except RuntimeError as e:
            logging.info(f"Frame ready emit failed: {e}")

    def play(self, url):
        if self.mpv_player:
            self.mpv_player.play(url)

    def stop(self):
        if self.mpv_player:
            self.mpv_player.stop()

    def set_paused(self, pause_state: bool):
        if self.mpv_player and self.mpv_player.pause != pause_state:
            self.mpv_player.pause = pause_state

    def set_muted(self, mute_state: bool):
        if self.mpv_player and self.mpv_player.mute != mute_state:
            self.mpv_player.mute = mute_state

    def seek_relative(self, seconds):
        if self.mpv_player:
            current_time = self.mpv_player.time_pos
            if current_time is not None:
                self.mpv_player.time_pos = current_time + seconds

    def seek_to_start(self):
        if self.mpv_player:
            self.mpv_player.time_pos = 0
            self.mpv_player.pause = False

    def length(self):
        if self.mpv_player:
            return self.mpv_player.duration
        return None

    def cleanup(self):
        self.stop()
        if self.mpv_ctx:
            self.mpv_ctx.free()
        if self.mpv_player:
            self.mpv_player.terminate()

    def initializeGL(self):
        self.mpv_player = mpv.MPV(
            vo="libmpv",
            profile="fast",
            wid="0",
            keep_open="yes",
            sub_visibility=False,
            osd_level=0,
            hwdec="no",
            vd_lavc_fast=True,
        )
        self.mpv_player["vf"] = "scale=-2:240,fps=12"
        self.mpv_player["framedrop"] = "decoder"
        self.mpv_player["video-unscaled"] = "no"
        self.mpv_player["panscan"] = 1.0

        # Grab the native OpenGL function pointer from Qt
        def get_proc_address(_, name):
            ctx = QOpenGLContext.currentContext()
            return int(ctx.getProcAddress(name)) if ctx else 0

        # Create the rendering context binding mpv to this specific OpenGL widget
        self.proc_address_fn = mpv.MpvGlGetProcAddressFn(get_proc_address)
        self.mpv_ctx = mpv.MpvRenderContext(
            self.mpv_player,
            "opengl",
            opengl_init_params={"get_proc_address": self.proc_address_fn},
        )

        # Whenever mpv receives a frame, trigger our signal
        self.mpv_ctx.update_cb = self._emit_frame_ready

        self.set_muted(True)

    def paintGL(self):
        if self.mpv_ctx:
            ratio = self.devicePixelRatio()
            w = int(self.width() * ratio)
            h = int(self.height() * ratio)

            fbo = int(self.defaultFramebufferObject())

            # Tell mpv to render into our widget's active FBO
            self.mpv_ctx.render(flip_y=True, opengl_fbo={"w": w, "h": h, "fbo": fbo})

            # Draw mask (black corners, transparent rounded center)
            painter = QPainter(self)
            full = QPainterPath()
            full.addRect(self.rect())
            radius = int(self.width() * 0.03)
            rounded = QPainterPath()
            rounded.addRoundedRect(self.rect(), radius, radius)
            mask = full.subtracted(rounded)
            painter.fillPath(mask, QColor(BG_COLOR))
            painter.end()
