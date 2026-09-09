from PySide6.QtWidgets import (
    QPushButton,
    QDialog,
    QFormLayout,
    QSpinBox,
    QComboBox,
    QCheckBox,
)

from style import (
    BUTTON_STYLE_PURPLE,
    CHECKBOX_STYLE,
    DROPDOWN_STYLE,
    FORM_ELEMENT_STYLE,
)


class MixDialog(QDialog):
    def __init__(self, parent=None, prefixes=None):
        super().__init__(parent)
        self.setWindowTitle("Mix Settings")
        self.resize(320, 220)

        layout = QFormLayout(self)
        form_element_width = 150

        self.checkbox_sample = QCheckBox()
        self.checkbox_sample.setStyleSheet(CHECKBOX_STYLE)
        self.checkbox_sample.setChecked(True)
        self.checkbox_sample.toggled.connect(self._sample_changed)
        layout.addRow("Sample:", self.checkbox_sample)

        self.spin_base_duration = QSpinBox()
        self.spin_base_duration.setFixedWidth(form_element_width)
        self.spin_base_duration.setStyleSheet(FORM_ELEMENT_STYLE)
        self.spin_base_duration.setRange(1, 3600)
        self.spin_base_duration.setValue(60)
        layout.addRow("Base duration (s):", self.spin_base_duration)

        self.spin_spread_duration = QSpinBox()
        self.spin_spread_duration.setFixedWidth(form_element_width)
        self.spin_spread_duration.setStyleSheet(FORM_ELEMENT_STYLE)
        self.spin_spread_duration.setRange(0, 3600)
        self.spin_spread_duration.setValue(5)
        layout.addRow("Spread duration (s):", self.spin_spread_duration)

        self.spin_max_videos = QSpinBox()
        self.spin_max_videos.setFixedWidth(form_element_width)
        self.spin_max_videos.setStyleSheet(FORM_ELEMENT_STYLE)
        self.spin_max_videos.setRange(1, 100)
        self.spin_max_videos.setValue(5)
        layout.addRow("Max videos:", self.spin_max_videos)

        self.combo_prefix = QComboBox()
        self.combo_prefix.setFixedWidth(form_element_width)
        self.combo_prefix.setStyleSheet(DROPDOWN_STYLE)
        self.combo_prefix.addItems(prefixes)
        layout.addRow("Prefix:", self.combo_prefix)

        self.btn_mix = QPushButton("⚡ Mix")
        self.btn_mix.setStyleSheet(BUTTON_STYLE_PURPLE)
        self.btn_mix.clicked.connect(self.accept)
        layout.addRow(self.btn_mix)

    def _sample_changed(self, value):
        self.spin_base_duration.setEnabled(value)
        self.spin_spread_duration.setEnabled(value)

    def get_data(self):
        return {
            "sample": self.checkbox_sample.isChecked(),
            "base_duration": self.spin_base_duration.value(),
            "spread_duration": self.spin_spread_duration.value(),
            "max_videos": self.spin_max_videos.value(),
            "prefix": self.combo_prefix.currentText(),
        }
