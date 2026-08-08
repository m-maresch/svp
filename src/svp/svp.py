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
    QSplitter,
)
from PySide6.QtCore import Qt, QEvent, QTimer, QDir
from PySide6.QtGui import QKeySequence, QShortcut

from player import open_with_player

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
        self.setStyleSheet("background-color: #121214;")

        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        width = int(screen_geometry.width())
        height = int(screen_geometry.height())
        self.resize(width, height)

        self.video_extensions = (".mp4", ".mov")
        self.all_files = []
        self.selected_path = ""
        self.prefix = ""
        self.playback = True
        self.skip_related = 0

        self.container_widget = QWidget()
        self.container_widget.setMaximumHeight(height * 0.95)
        self.setCentralWidget(self.container_widget)
        self.outer_layout = QVBoxLayout(self.container_widget)

        # Control Bar
        self.controls = QHBoxLayout()

        self.btn_restart = QPushButton("↻ Restart")
        self.btn_restart.clicked.connect(lambda: self._restart_previews())
        self.btn_restart.setStyleSheet(BUTTON_STYLE_RED)
        self.btn_toggle_playback = QPushButton("⏸ Pause")
        self.btn_toggle_playback.clicked.connect(lambda: self._toggle_playback())
        self.btn_toggle_playback.setStyleSheet(BUTTON_STYLE_RED)
        self.btn_plus_1_min = QPushButton("▶▶ 1 min")
        self.btn_plus_1_min.clicked.connect(lambda: self._jump_minutes(1))
        self.btn_plus_1_min.setStyleSheet(BUTTON_STYLE_BLUE)
        self.btn_plus_5_min = QPushButton("▶▶ 5 min")
        self.btn_plus_5_min.clicked.connect(lambda: self._jump_minutes(5))
        self.btn_plus_5_min.setStyleSheet(BUTTON_STYLE_BLUE)
        self.btn_hide_related = QPushButton("Hide related")
        self.btn_hide_related.clicked.connect(lambda: self._hide_related())
        self.btn_hide_related.setStyleSheet(BUTTON_STYLE_BLUE)
        self.btn_toggle_library = QPushButton("Hide library")
        self.btn_toggle_library.clicked.connect(lambda: self._toggle_library())
        self.btn_toggle_library.setStyleSheet(BUTTON_STYLE_BLUE)
        self.btn_randomize = QPushButton("🎲 Randomize")
        self.btn_randomize.setStyleSheet(BUTTON_STYLE_PURPLE)
        self.btn_randomize.clicked.connect(self._randomize)
        self.checkbox_randomize_related = QCheckBox("Include related")
        self.checkbox_randomize_related.setStyleSheet(CHECKBOX_STYLE)
        self.checkbox_randomize_related.setChecked(True)

        self.controls.addWidget(self.btn_restart)
        self.controls.addWidget(self.btn_toggle_playback)
        self.controls.addWidget(self.btn_plus_1_min)
        self.controls.addWidget(self.btn_plus_5_min)
        self.controls.addStretch(1)
        self.controls.addWidget(self.btn_hide_related)
        self.controls.addWidget(self.btn_toggle_library)
        self.controls.addWidget(self.btn_randomize)
        self.controls.addWidget(self.checkbox_randomize_related)
        self.outer_layout.addLayout(self.controls)

        # --- Left Side: Video Previews ---
        self.previews_container = QWidget()
        self.previews_layout = QVBoxLayout(self.previews_container)
        self.previews_layout.setContentsMargins(0, 0, 0, 0)
        self.previews_layout.setSpacing(0)

        # Related Grid
        self.related_header = QLabel("Related")
        self.related_header.setStyleSheet(HEADER_STYLE)
        self.previews_layout.addWidget(self.related_header)

        self.related_line = QFrame()
        self.related_line.setFrameShape(QFrame.HLine)
        self.related_line.setFrameShadow(QFrame.Sunken)
        self.related_line.setStyleSheet("background-color: #444; margin: 10px 5px;")
        self.previews_layout.addWidget(self.related_line)

        self.related_previews = []
        self.related_widget = QWidget()
        self.related_layout = QGridLayout(self.related_widget)
        self.related_layout.setSpacing(2)

        related_preview_max_width = width * 1 / self.related_previews_per_row
        for i in range(self.related_rows * self.related_previews_per_row):
            preview = VideoPreviewWidget(i, max_width=related_preview_max_width)
            self.related_layout.addWidget(
                preview,
                i // self.related_previews_per_row,
                i % self.related_previews_per_row,
            )
            self.related_previews.append(preview)

        self.previews_layout.addWidget(self.related_widget)

        # Library Grid
        self.library_header = QLabel("Library")
        self.library_header.setStyleSheet(HEADER_STYLE)
        self.previews_layout.addWidget(self.library_header)

        self.library_line = QFrame()
        self.library_line.setFrameShape(QFrame.HLine)
        self.library_line.setFrameShadow(QFrame.Sunken)
        self.library_line.setStyleSheet("background-color: #444; margin: 10px 5px;")
        self.previews_layout.addWidget(self.library_line)

        self.library_previews = []
        self.library_widget = QWidget()
        self.library_layout = QGridLayout(self.library_widget)
        self.library_layout.setSpacing(2)

        library_preview_max_width = width * 1 / self.library_previews_per_row
        for i in range(self.library_rows * self.library_previews_per_row):
            preview = VideoPreviewWidget(
                i + (self.related_rows * self.related_previews_per_row),
                max_width=library_preview_max_width,
            )
            self.library_layout.addWidget(
                preview,
                i // self.library_previews_per_row,
                i % self.library_previews_per_row,
            )
            self.library_previews.append(preview)

        self.previews_layout.addWidget(self.library_widget)
        # Add a stretch at the bottom so grids stay tight if the window expands
        self.previews_layout.addStretch()

        # --- Right Side: Files List ---
        self.files_widget = QWidget()
        self.files_layout = QVBoxLayout(self.files_widget)
        self.files_widget.setFixedWidth(150)
        self.btn_reset_files = QPushButton("↩ Clear")
        self.btn_reset_files.setStyleSheet(BUTTON_STYLE_RED)
        self.dropdown_files = QComboBox()
        self.dropdown_files.setStyleSheet(DROPDOWN_STYLE)
        self.dropdown_files.currentIndexChanged.connect(self._filter_files_list)
        self.btn_reset_files.clicked.connect(
            lambda: self.dropdown_files.setCurrentIndex(0)
        )
        self.files_list_widget = QListWidget()
        self.files_list_widget.itemClicked.connect(self._handle_files_list_click)
        self.files_list_widget.itemDoubleClicked.connect(
            self._handle_files_list_double_click
        )
        self.files_layout.addWidget(self.dropdown_files)
        self.files_layout.addWidget(self.files_list_widget)
        self.files_layout.addWidget(self.btn_reset_files)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.previews_container)
        self.splitter.addWidget(self.files_widget)
        self.outer_layout.addWidget(self.splitter)

        self._hide_related()

        self.toggle_playback_shortcut = QShortcut(QKeySequence("Space"), self)
        self.toggle_playback_shortcut.activated.connect(self._toggle_playback)
        self.restart_previews_shortcut = QShortcut(QKeySequence("Left"), self)
        self.restart_previews_shortcut.activated.connect(self._restart_previews)
        self.jump_shortcut = QShortcut(QKeySequence("Right"), self)
        self.jump_shortcut.activated.connect(lambda: self._jump_minutes(1))
        self.randomize_shortcut = QShortcut(QKeySequence("R"), self)
        self.randomize_shortcut.activated.connect(self._randomize)
        self.reset_files_shortcut = QShortcut(QKeySequence("C"), self)
        self.reset_files_shortcut.activated.connect(
            lambda: self.dropdown_files.setCurrentIndex(0)
        )
        self.quit_shortcut = QShortcut(QKeySequence("Q"), self)
        self.quit_shortcut.activated.connect(self.close)

        if self.current_folder:
            QTimer.singleShot(250, self._initial_refresh)
        else:
            QTimer.singleShot(250, self._initial_pick_folder)

    def _restart_previews(self):
        for preview in self.related_previews + self.library_previews:
            preview.restart()
            self._set_playback(self.playback)

    def _jump_minutes(self, number):
        for preview in self.related_previews + self.library_previews:
            preview.jump_seconds(number * 60)

    def _toggle_playback(self):
        self.playback = not self.playback
        if self.playback:
            self.btn_toggle_playback.setText("⏸ Pause")
        else:
            self.btn_toggle_playback.setText("▶ Play")
        self._set_playback(self.playback)

    def _set_playback(self, active):
        for preview in self.related_previews + self.library_previews:
            preview.set_playback(active)

    def _hide_related(self):
        self.related_header.hide()
        self.related_line.hide()
        self.related_widget.hide()
        self.btn_hide_related.hide()
        self.selected_path = ""

    def _toggle_library(self):
        if self.library_widget.isVisible():
            self.library_header.hide()
            self.library_line.hide()
            self.library_widget.hide()
            self.btn_toggle_library.setText("Show library")
        else:
            self.library_header.show()
            self.library_line.show()
            self.library_widget.show()
            self.btn_toggle_library.setText("Hide library")

    def _randomize(self):
        if not self.all_files:
            return

        if self.selected_path:
            self._update_related(randomize_first=True)

        current_related_videos = [
            p.file_path for p in self.related_previews if p.file_path is not None
        ]
        previous_library_videos = [
            p.file_path for p in self.library_previews if p.file_path is not None
        ]

        candidates = self.all_files
        if len(candidates) > 2 * len(current_related_videos + previous_library_videos):
            candidates = [
                f
                for f in self.all_files
                if (f not in (current_related_videos + previous_library_videos))
            ]

        selection = random.sample(
            candidates,
            min(len(candidates), self.library_rows * self.library_previews_per_row),
        )

        for i, preview in enumerate(self.library_previews):
            path = selection[i] if i < len(selection) else None
            preview.load_video(path)

    def _filter_files_list(self):
        selected_prefix = self.dropdown_files.currentText()
        self._populate_files_list(selected_prefix if selected_prefix != "All" else None)

    def _populate_files_list(self, pref=None):
        self.files_list_widget.clear()
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
            self.files_list_widget.addItem(item)

    def _handle_files_list_click(self, item):
        self.selected_path = item.data(Qt.UserRole)
        self.prefix = _prefix(self.selected_path)
        self.skip_related = 0
        self._update_related()

    def _handle_files_list_double_click(self, item):
        path = item.data(Qt.UserRole)
        if path:
            open_with_player(path)

    def _update_related(self, randomize_first: bool = False):
        # Determine matches
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
        self.btn_hide_related.setVisible(True)

        num_to_show = min(
            len(matches), self.related_rows * self.related_previews_per_row
        )

        if self.checkbox_randomize_related.isChecked():
            previous_related_videos = [
                preview.file_path
                for preview in self.related_previews
                if preview.file_path is not None
            ]

            candidates = matches
            if len(candidates) > 2 * len(previous_related_videos):
                candidates = [m for m in matches if m not in previous_related_videos]

            selection = random.sample(candidates, num_to_show)
            selection.sort()
        else:
            match = re.match(r"([A-Za-z-]+)(\d+)", os.path.basename(self.selected_path))
            selection = []
            if match:
                pref = match.group(1)
                numb = int(match.group(2)) + self.skip_related

                next = [
                    pref + str(n) + "." for n in range(numb + 1, numb + num_to_show + 1)
                ]
                for n in next:
                    next_match = [m for m in matches if n in m]
                    if next_match:
                        selection.append(next_match[0])

                self.skip_related += num_to_show - 1
            else:
                logging.info("No more next related")

        # Fill the previews
        if randomize_first and matches and self.checkbox_randomize_related.isChecked():
            shown = {p.file_path for p in self.related_previews if p.file_path}
            candidates = [m for m in matches if (m not in shown and m not in selection)]
            choice = random.choice(candidates) if candidates else None
            if choice:
                self.related_previews[0].load_video(choice)
            else:
                self.related_previews[0].load_video(self.selected_path)
        elif randomize_first and not self.checkbox_randomize_related.isChecked():
            self.related_previews[0].load_video(selection[0])
            selection = selection[1:]
            self.skip_related += 1
        else:
            self.related_previews[0].load_video(self.selected_path)

        for i, preview in enumerate(self.related_previews[1:]):
            path = selection[i] if i < len(selection) else None
            preview.load_video(path)

            if path:
                preview.show()
            else:
                preview.hide()

    def _initial_pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Videos")
        if folder:
            self.current_folder = QDir.toNativeSeparators(os.path.abspath(folder))
            self._initial_refresh()
        else:
            QApplication.quit()

    def _initial_refresh(self):
        self._populate_files_list()
        self.dropdown_files.addItems(
            ["All"] + list(sorted(_all_prefixes(self.all_files)))
        )
        self._randomize()

    def changeEvent(self, event):
        """Detects focus changes to pause/resume all videos."""
        if event.type() == QEvent.ActivationChange:
            is_active = self.isActiveWindow()
            self._set_playback(is_active)

        super().changeEvent(event)

    def closeEvent(self, event):
        for preview in self.related_previews + self.library_previews:
            preview.cleanup()

        self.related_previews.clear()
        self.library_previews.clear()

        super().closeEvent(event)


def _prefix(name):
    return re.sub(r"\d+", "", os.path.splitext(os.path.basename(name))[0]).strip()


def _all_prefixes(names):
    return set([_prefix(n) for n in names])


def _file_sort_key(name):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)]
