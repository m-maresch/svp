import logging
import re
import os
import random


from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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
    QScrollArea,
    QSplitter,
)
from PySide6.QtCore import Qt, QEvent, QTimer, QDir

from player import open_file_with_player

from preview import VideoPreviewWidget

from style import (
    HEADER_STYLE,
    BUTTON_STYLE_BLUE,
    BUTTON_STYLE_RED,
    BUTTON_STYLE_PURPLE,
    CHECKBOX_STYLE,
    DROPDOWN_STYLE,
)


class SVP(QMainWindow):
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

        self.setWindowTitle("Smart Video Previewer")
        self.resize(1600, 900)
        self.setStyleSheet("background-color: #121214;")
        self.video_extensions = (".mp4", ".mov")
        self.all_files = []  # Store full sorted list for "Related" logic
        self.selected_path = ""
        self.prefix = ""

        self.container_widget = QWidget()
        self.outer_layout = QVBoxLayout(self.container_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.container_widget)
        self.setCentralWidget(self.scroll_area)

        # Control Bar
        self.controls = QHBoxLayout()

        self.btn_restart = QPushButton("↻ Restart")
        self.btn_restart.clicked.connect(lambda: self.restart_previews())
        self.btn_restart.setStyleSheet(BUTTON_STYLE_RED)
        self.btn_plus_1_min = QPushButton("▶▶ 1 min")
        self.btn_plus_1_min.clicked.connect(lambda: self.jump_minutes(1))
        self.btn_plus_1_min.setStyleSheet(BUTTON_STYLE_BLUE)
        self.btn_plus_5_min = QPushButton("▶▶ 5 min")
        self.btn_plus_5_min.clicked.connect(lambda: self.jump_minutes(5))
        self.btn_plus_5_min.setStyleSheet(BUTTON_STYLE_BLUE)
        self.btn_randomize = QPushButton("🎲 Randomize")
        self.btn_randomize.setStyleSheet(BUTTON_STYLE_PURPLE)
        self.btn_randomize.clicked.connect(self.randomize)
        self.cb_randomize_related = QCheckBox("Include related")
        self.cb_randomize_related.setStyleSheet(CHECKBOX_STYLE)
        self.cb_randomize_related.setChecked(True)

        self.controls.addWidget(self.btn_restart)
        self.controls.addWidget(self.btn_plus_1_min)
        self.controls.addWidget(self.btn_plus_5_min)
        self.controls.addStretch(1)
        self.controls.addWidget(self.btn_randomize)
        self.controls.addWidget(self.cb_randomize_related)
        self.outer_layout.addLayout(self.controls)

        self.splitter = QSplitter(Qt.Horizontal)

        # --- Left Side: Structured Content Area ---
        self.grid_container = QWidget()
        self.container_layout = QVBoxLayout(self.grid_container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        self.related_header = QLabel("Related")
        self.related_header.setStyleSheet(HEADER_STYLE)
        self.container_layout.addWidget(self.related_header)

        self.related_line = QFrame()
        self.related_line.setFrameShape(QFrame.HLine)
        self.related_line.setFrameShadow(QFrame.Sunken)
        self.related_line.setStyleSheet("background-color: #444; margin: 10px 5px;")
        self.container_layout.addWidget(self.related_line)

        # 1. Related Content Grid
        self.related_previews = []
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

        self.library_header = QLabel("Library")
        self.library_header.setStyleSheet(HEADER_STYLE)
        self.container_layout.addWidget(self.library_header)

        # 2. Add the Divider (Horizontal Line)
        self.library_line = QFrame()
        self.library_line.setFrameShape(QFrame.HLine)
        self.library_line.setFrameShadow(QFrame.Sunken)
        self.library_line.setStyleSheet("background-color: #444; margin: 10px 5px;")
        self.container_layout.addWidget(self.library_line)

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
        self.files_widget = QWidget()
        self.files_layout = QVBoxLayout(self.files_widget)
        self.files_widget.setFixedWidth(150)
        self.btn_reset = QPushButton("↩ Clear")
        self.btn_reset.setStyleSheet(BUTTON_STYLE_RED)
        self.dropdown = QComboBox()
        self.dropdown.setStyleSheet(DROPDOWN_STYLE)
        self.dropdown.currentIndexChanged.connect(self.filter_list)
        self.btn_reset.clicked.connect(lambda: self.dropdown.setCurrentIndex(0))
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(
            self.handle_list_click
        )  # Single click to update "Related"
        self.list_widget.itemDoubleClicked.connect(self.handle_list_double_click)
        self.files_layout.addWidget(self.dropdown)
        self.files_layout.addWidget(self.list_widget)
        self.files_layout.addWidget(self.btn_reset)

        self.splitter.addWidget(self.grid_container)
        self.splitter.addWidget(self.files_widget)
        self.outer_layout.addWidget(self.splitter)

        self.related_header.hide()
        self.related_line.hide()
        self.related_widget.hide()

        if self.current_folder:
            QTimer.singleShot(250, self.initial_refresh)
        else:
            QTimer.singleShot(250, self.initial_pick_folder)

    def populate_list_view(self, pref=None):
        self.list_widget.clear()
        files = [
            f
            for f in os.listdir(self.current_folder)
            if f.lower().endswith(self.video_extensions)
        ]
        self.all_files = sorted(
            [os.path.join(self.current_folder, f) for f in files], key=_file_sort_key
        )

        for path in self.all_files:
            if pref and pref != _prefix(path):
                continue

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
        # Determine if we have matches
        matches = []
        if self.all_files and self.prefix:
            matches = [
                f
                for f in self.all_files
                if self.prefix == _prefix(f) and (self.selected_path != f)
            ]
            matches = sorted(matches)

        self.related_header.setVisible(True)
        self.related_line.setVisible(True)
        self.related_widget.setVisible(True)

        # Fill the previews
        num_to_show = min(
            len(matches), self.related_rows * self.related_previews_per_row
        )

        if self.cb_randomize_related.isChecked():
            selection = random.sample(matches, num_to_show)
            selection.sort()
        else:
            match = re.match(r"([A-Za-z]+)(\d+)", os.path.basename(self.selected_path))
            if match:
                pref = match.group(1)
                numb = int(match.group(2))

                selection = []
                next = [
                    pref + str(n) + "." for n in range(numb + 1, numb + num_to_show + 1)
                ]
                for n in next:
                    next_match = [m for m in matches if n in m]
                    if next_match:
                        selection.append(next_match[0])
            else:
                logging.info("No more next related")
                return

        self.related_previews[0].load_video(self.selected_path)
        for i, preview in enumerate(self.related_previews[1:]):
            path = selection[i] if i < len(selection) else None
            preview.load_video(path)

            if path:
                preview.show()
            else:
                preview.hide()

    def handle_list_double_click(self, item):
        """Opens the video in the default system player on double-click."""
        path = item.data(Qt.UserRole)
        if path:
            open_file_with_player(path)

    def filter_list(self):
        selected_prefix = self.dropdown.currentText()
        self.populate_list_view(selected_prefix if selected_prefix != "All" else None)

    def randomize(self):
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

    def restart_previews(self):
        for preview in self.related_previews + self.library_previews:
            preview.restart()

    def jump_minutes(self, number):
        for preview in self.related_previews + self.library_previews:
            preview.jump_seconds(number * 60)

    def initial_pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Videos")
        if folder:
            self.current_folder = QDir.toNativeSeparators(os.path.abspath(folder))
            self.initial_refresh()
        else:
            QApplication.quit()

    def initial_refresh(self):
        self.populate_list_view()
        self.dropdown.addItems(["All"] + list(sorted(_all_prefixes(self.all_files))))
        self.randomize()

    def changeEvent(self, event):
        """Detects focus changes to pause/resume all videos."""
        if event.type() == QEvent.ActivationChange:
            is_active = self.isActiveWindow()
            for preview in self.related_previews + self.library_previews:
                preview.set_playback(is_active)

        super().changeEvent(event)


def _prefix(name):
    return re.sub(r"\d+", "", os.path.splitext(os.path.basename(name))[0]).strip()


def _all_prefixes(names):
    return set([_prefix(n) for n in names])


def _file_sort_key(name):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)]
