import os

from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QEvent, QTimer

from player import open_file_with_player

from style import MASK_OVERLAY_STYLE

from video import MPVVideoWidget


class VideoPreviewWidget(QWidget):
    """Individual grid item with video and double-click support."""

    def __init__(self, idx, parent=None):
        super().__init__(parent)
        self.idx = idx

        self.file_path = ""
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)

        self.setMaximumWidth(800)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

        self.video_widget = MPVVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.mask_overlay = QLabel()
        self.mask_overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.mask_overlay.setStyleSheet(MASK_OVERLAY_STYLE)

        # This allows the widget to catch double clicks
        self.video_widget.installEventFilter(self)

        self.video_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.show_duration_ms = 10000
        self.skip_interval_s = 60  # 1 minute

        self.jump_timer = QTimer(self)
        self.jump_timer.timeout.connect(lambda: self.jump_seconds(self.skip_interval_s))

        self.label = QLabel("-")
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-size: 10px; color: #777;")

        self.layout.addWidget(self.video_widget, 0, 0)
        self.layout.addWidget(self.mask_overlay, 0, 0)
        self.layout.addWidget(self.label, 1, 0)

        self.setMouseTracking(True)

        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.setInterval(2000)
        self.hover_timer.timeout.connect(lambda: self.video_widget.setMuted(False))

    def event(self, event):
        if event.type() == QEvent.Type.HoverEnter:
            self.hover_timer.start()
        elif event.type() == QEvent.Type.HoverLeave:
            if self.hover_timer.isActive():
                self.hover_timer.stop()
            self.video_widget.setMuted(True)
        return super().event(event)

    def mouseDoubleClickEvent(self, event):
        if self.file_path:
            open_file_with_player(self.file_path)

    def load_video(self, file_path):
        self.file_path = file_path

        self.video_widget.stop()
        self.jump_timer.stop()

        if file_path:
            self.video_widget.play(self.file_path)
            self.video_widget.show()
            self.label.show()

            QTimer.singleShot(1500, lambda: self.video_widget.seekRelative(10))

            # Start the jumping cycle
            QTimer.singleShot(
                self.idx * 200, lambda: self.jump_timer.start(self.show_duration_ms)
            )
            self.label.setText(os.path.basename(file_path))
        else:
            self.video_widget.hide()
            self.label.hide()

    def restart(self):
        self.video_widget.seekToStart()

    def jump_seconds(self, number):
        self.video_widget.seekRelative(number)

    def set_playback(self, active: bool):
        """Handle App Focus Changes"""
        if self.file_path:
            if active:
                self.video_widget.setPaused(False)
                self.jump_timer.start(self.show_duration_ms)
            else:
                self.video_widget.setPaused(True)
                self.jump_timer.stop()

    def resizeEvent(self, event):
        """Force the widget to maintain a 16:9 aspect ratio based on its width."""
        width = self.width()
        target_height = int(width * 9 / 16)

        if self.height() != target_height:
            label_height = self.label.sizeHint().height()
            self.setFixedHeight(target_height + label_height)

        super().resizeEvent(event)
