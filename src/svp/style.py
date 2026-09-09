BG_COLOR = "#121214"

HEADER_STYLE = """
QLabel {
    font-size: 24px;
    font-weight: bold;
    color: #ECEFF1;
    padding-top: 8px;
    padding-bottom: 8px;
}
"""

BUTTON_STYLE_BLUE = """
QPushButton {
    background-color: #228be6;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #1c7ed6;
}
"""

BUTTON_STYLE_RED = """
QPushButton {
    background-color: #e03131;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #c92a2a;
}
"""

BUTTON_STYLE_PURPLE = """
QPushButton {
    background-color: #7048e8;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #5f3dc4;
}
"""

CHECKBOX_STYLE = """
QCheckBox {
    color: white;
    spacing: 4px;
}
QCheckBox::indicator {
    background-color: #2b2c30;
    border: 1px solid #373a40;
    border-radius: 4px;
    width: 14px;
    height: 14px;
}
QCheckBox::indicator:hover {
    border-color: #228be6; /* Blue border on hover */
}
QCheckBox::indicator:checked {
    background-color: #228be6; /* Fills blue when checked */
    border-color: #228be6;
}
"""

DROPDOWN_STYLE = """
QComboBox {
    background-color: #2b2c30;
    color: white;
    border: 1px solid #373a40;
    border-radius: 4px;
    padding: 5px;
}
QComboBox:hover {
    border-color: #228be6; /* Blue border on hover */
}
"""

FORM_ELEMENT_STYLE = """
QSpinBox {
    background-color: #2b2c30;
    color: white;
    border: 1px solid #373a40;
    border-radius: 4px;
    padding: 5px;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 20px;
}
QSpinBox:disabled {
    background-color: #2d2d2d;
    color: #777777;
}
"""
