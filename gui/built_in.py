from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QStyle, QWidget


def icon(parent: QWidget, icon_name: str) -> QIcon:
    return QIcon(parent.style().standardIcon(getattr(QStyle, f'SP_{icon_name}')))
