import logging
import re
import sys
import os
import random
import subprocess
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QMainWindow,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QSplitter,
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QUrl, QEvent, QTimer, QDir


class VideoPreviewWidget(QWidget):
    """Individual grid item with video and double-click support."""

    def __init__(self, idx, parent=None):
        super().__init__(parent)
        self.idx = idx

        self.file_path = ""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)

        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_widget.setStyleSheet(
            "background-color: #000; border: 1px solid #444;"
        )

        self.video_widget.setAspectRatioMode(Qt.IgnoreAspectRatio)

        # This allows the widget to catch double clicks
        self.video_widget.installEventFilter(self)

        self.video_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setPlaybackRate(1.0)
        self.audio_output = QAudioOutput()
        self.audio_output.setMuted(True)
        self.media_player.setAudioOutput(self.audio_output)

        self.jump_timer = QTimer(self)
        self.jump_timer.timeout.connect(self.perform_jump)

        self.show_duration = 10000
        self.skip_interval = 60000  # 1 minute (ms)

        self.label = QLabel("-")
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-size: 10px; color: #777;")

        self.layout.addWidget(self.video_widget)
        self.layout.addWidget(self.label)

        self.setMouseTracking(True)

    def event(self, event):
        if event.type() == QEvent.Type.HoverEnter:
            self.audio_output.setMuted(False)
        elif event.type() == QEvent.Type.HoverLeave:
            self.audio_output.setMuted(True)
        return super().event(event)

    def mouseDoubleClickEvent(self, event):
        if self.file_path:
            open_file_with_player(self.file_path)

    def load_video(self, file_path):
        self.file_path = file_path

        self.media_player.stop()
        self.jump_timer.stop()

        if file_path:
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.media_player.setLoops(QMediaPlayer.Infinite)
            self.media_player.play()

            self.video_widget.show()
            self.label.show()

            # Start the jumping cycle
            QTimer.singleShot(
                self.idx * 200, lambda: self.jump_timer.start(self.show_duration)
            )
            self.label.setText(os.path.basename(file_path))
        else:
            self.video_widget.hide()
            self.label.hide()

    def perform_jump(self):
        if not self.media_player.isSeekable():
            return

        current_pos = self.media_player.position()
        video_duration = self.media_player.duration()

        new_pos = current_pos + self.skip_interval

        # If we hit the end of the video, restart from the beginning
        if new_pos >= video_duration:
            new_pos = 0

        self.media_player.setPosition(new_pos)

    def set_playback(self, active: bool):
        """Handle App Focus Changes"""
        if self.file_path:
            if active:
                self.media_player.play()
                self.jump_timer.start(self.show_duration)
            else:
                self.media_player.pause()
                self.jump_timer.stop()

    def resizeEvent(self, event):
        """Force the widget to maintain a 16:9 aspect ratio based on its width."""
        width = self.width()
        target_height = int(width * 9 / 16)

        if self.height() != target_height:
            label_height = self.label.sizeHint().height()
            self.setFixedHeight(target_height + label_height)

        super().resizeEvent(event)


class VideoCanvas(QMainWindow):
    def __init__(
        self,
        current_folder,
        related_rows,
        related_previews_per_row,
        library_rows,
        library_previews_per_row,
    ):
        super().__init__()
        self.current_folder = current_folder
        self.related_rows = related_rows
        self.related_previews_per_row = related_previews_per_row
        self.library_rows = library_rows
        self.library_previews_per_row = library_previews_per_row

        self.setWindowTitle("Video Manager")
        self.resize(1600, 900)
        self.video_extensions = (".mp4", ".mov")
        self.all_files = []  # Store full sorted list for "Related" logic
        self.selected_path = ""
        self.prefix = ""

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.outer_layout = QVBoxLayout(self.central_widget)

        # Control Bar
        self.controls = QHBoxLayout()
        self.btn_refresh = QPushButton("🎲 Randomize")
        self.btn_refresh.clicked.connect(self.load_random_batch)
        self.controls.addWidget(self.btn_refresh)
        self.outer_layout.addLayout(self.controls)

        self.splitter = QSplitter(Qt.Horizontal)
        self.outer_layout.addWidget(self.splitter)

        # --- Left Side: Structured Content Area ---
        self.grid_container = QWidget()
        self.container_layout = QVBoxLayout(self.grid_container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        self.related_previews = []

        # 1. Related Content Grid
        self.related_widget = QWidget()
        self.related_layout = QGridLayout(self.related_widget)
        self.related_layout.setSpacing(2)
        for i in range(self.related_rows * self.related_previews_per_row):
            preview = VideoPreviewWidget(i)
            self.related_layout.addWidget(
                preview,
                i // self.related_previews_per_row,
                i % self.related_previews_per_row,
            )
            self.related_previews.append(preview)

        self.container_layout.addWidget(self.related_widget)

        # 2. Add the Divider (Horizontal Line)
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setStyleSheet("background-color: #444; margin: 10px 5px;")
        self.container_layout.addWidget(self.line)

        # 3. Library Grid
        self.library_previews = []
        self.library_widget = QWidget()
        self.library_layout = QGridLayout(self.library_widget)
        self.library_layout.setSpacing(2)
        for i in range(self.library_rows * self.library_previews_per_row):
            preview = VideoPreviewWidget(
                i + (self.related_rows * self.related_previews_per_row)
            )
            self.library_layout.addWidget(
                preview,
                i // self.library_previews_per_row,
                i % self.library_previews_per_row,
            )
            self.library_previews.append(preview)

        self.container_layout.addWidget(self.library_widget)
        # Add a stretch at the bottom so grids stay tight if the window expands
        self.container_layout.addStretch()

        # --- Right Side: List View ---
        self.list_widget = QListWidget()
        self.list_widget.setFixedWidth(100)
        self.list_widget.itemClicked.connect(
            self.handle_list_click
        )  # Single click to update "Related"
        self.list_widget.itemDoubleClicked.connect(self.handle_list_double_click)

        self.splitter.addWidget(self.grid_container)
        self.splitter.addWidget(self.list_widget)
        self.outer_layout.addWidget(self.splitter)

        self.related_widget.hide()
        self.line.hide()

        if self.current_folder:
            QTimer.singleShot(250, self.refresh)
        else:
            QTimer.singleShot(250, self.initial_pick_folder)

    def populate_list_view(self):
        self.list_widget.clear()
        files = [
            f
            for f in os.listdir(self.current_folder)
            if f.lower().endswith(self.video_extensions)
        ]
        self.all_files = sorted(
            [os.path.join(self.current_folder, f) for f in files], key=file_sort_key
        )

        for path in self.all_files:
            item = QListWidgetItem(os.path.basename(path))
            item.setData(Qt.UserRole, path)
            self.list_widget.addItem(item)

    def handle_list_click(self, item):
        """Extract prefix and update the 'Related' top row."""
        self.selected_path = item.data(Qt.UserRole)
        filename = os.path.basename(self.selected_path)

        # 1. Strip extension
        name_no_ext = os.path.splitext(filename)[0]

        # 2. Strip all numbers to get the "Series" name (e.g., "Show01-Part2" -> "Show-Part")
        # \d matches any digit, '' replaces it with nothing
        self.prefix = re.sub(r"\d+", "", name_no_ext).strip()

        self.update_related_row()

    def update_related_row(self):
        # 1. Determine if we have matches
        matches = []
        if self.all_files and self.prefix:
            matches = [
                f
                for f in self.all_files
                if (
                    self.prefix
                    == re.sub(
                        r"\d+", "", os.path.splitext(os.path.basename(f))[0]
                    ).strip()
                )
                and (self.selected_path != f)
            ]
            matches = sorted(matches)

        # 2. Toggle visibility of the entire Related section and the Divider
        # If no prefix or no matches, hide it all
        has_enough_content = len(matches) >= 3
        self.related_widget.setVisible(has_enough_content)
        self.line.setVisible(has_enough_content)

        if not has_enough_content:
            # Clean up the media players to stop background processing
            for p in self.related_previews:
                p.load_video(None)
            return

        # 3. Fill the previews as usual
        num_to_show = min(
            len(matches), self.related_rows * self.related_previews_per_row
        )
        random_selection = random.sample(matches, num_to_show)
        random_selection.sort()

        self.related_previews[0].load_video(self.selected_path)
        for i, preview in enumerate(self.related_previews[1:]):
            path = random_selection[i] if i < len(random_selection) else None
            preview.load_video(path)

    def handle_list_double_click(self, item):
        """Opens the video in the default system player on double-click."""
        path = item.data(Qt.UserRole)
        if path:
            open_file_with_player(path)

    def load_random_batch(self):
        if not self.all_files:
            return

        if self.selected_path:
            self.update_related_row()

        selection = random.sample(
            self.all_files,
            min(len(self.all_files), self.library_rows * self.library_previews_per_row),
        )

        for i, preview in enumerate(self.library_previews):
            path = selection[i] if i < len(selection) else None
            preview.load_video(path)

    def initial_pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Videos")
        if folder:
            self.current_folder = QDir.toNativeSeparators(os.path.abspath(folder))
            self.refresh()
        else:
            QApplication.quit()

    def refresh(self):
        self.populate_list_view()
        self.load_random_batch()

    def changeEvent(self, event):
        """Detects focus changes to pause/resume all videos."""
        if event.type() == QEvent.ActivationChange:
            is_active = self.isActiveWindow()
            for preview in self.related_previews + self.library_previews:
                preview.set_playback(is_active)

        super().changeEvent(event)


def file_sort_key(name):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)]


def open_file_with_player(filepath):
    if sys.platform == "win32":
        os.startfile(filepath)
    elif sys.platform == "darwin":
        subprocess.call(
            ["open", "-a", "VLC", filepath, "--args", "--fullscreen", "--play-and-exit"]
        )
    else:
        subprocess.call(["xdg-open", filepath])


if __name__ == "__main__":
    os.environ["QT_LOGGING_RULES"] = "qt.multimedia.ffmpeg*=false"
    logging.basicConfig(level=logging.INFO)

    app = QApplication(sys.argv)

    folder_path = ""
    if len(sys.argv) > 1:
        folder = sys.argv[1]
        folder_path = QDir.toNativeSeparators(os.path.abspath(folder))

    related_rows = 1
    related_previews_per_row = 6
    library_rows = 2
    library_previews_per_row = 6
    if len(sys.argv) == 6:
        related_rows = int(sys.argv[2])
        related_previews_per_row = int(sys.argv[3])
        library_rows = int(sys.argv[4])
        library_previews_per_row = int(sys.argv[5])

    logging.info(
        f"Using related grid={related_rows}x{related_previews_per_row} and library grid={library_rows}x{library_previews_per_row}"
    )

    window = VideoCanvas(
        folder_path,
        related_rows,
        related_previews_per_row,
        library_rows,
        library_previews_per_row,
    )
    window.show()

    sys.exit(app.exec())
