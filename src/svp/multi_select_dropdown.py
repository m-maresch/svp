from PySide6.QtCore import Signal
from PySide6.QtWidgets import QToolButton, QMenu, QWidgetAction, QCheckBox

from style import DROPDOWN_CHECKBOX_STYLE


class MultiSelectDropdown(QToolButton):
    selectionChanged = Signal(list)

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setText("Select options")
        self.setPopupMode(QToolButton.InstantPopup)

        self.selected_order = []

        self.menu = QMenu(self)
        self.menu.setStyleSheet(DROPDOWN_CHECKBOX_STYLE)

        for item in items:
            checkbox = QCheckBox(item)
            checkbox.stateChanged.connect(
                lambda state, it=item: self._on_toggled(it, state)
            )

            action = QWidgetAction(self.menu)
            action.setDefaultWidget(checkbox)
            self.menu.addAction(action)

        self.setMenu(self.menu)

    def _on_toggled(self, item, state):
        if state and item not in self.selected_order:
            self.selected_order.append(item)
        elif not state and item in self.selected_order:
            self.selected_order.remove(item)

        self.setText(
            ", ".join(self.selected_order) if self.selected_order else "Select options"
        )
        self.selectionChanged.emit(self.selected_order)

    def selected(self):
        return self.selected_order.copy()
