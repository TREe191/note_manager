"""Visual styling for the PySide6 desktop interface."""

DARK_STYLESHEET = """
QMainWindow {
    background: #1e1f22;
    color: #d8d8dc;
}
QWidget {
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 14px;
}
QLineEdit, QPlainTextEdit {
    background: #26282d;
    border: 1px solid #3a3d45;
    border-radius: 4px;
    color: #e7e8eb;
    padding: 8px;
    selection-background-color: #365a88;
}
QLineEdit:focus, QPlainTextEdit:focus {
    border-color: #6397d0;
}
QPushButton {
    background: #356b9f;
    border: 1px solid #4e82b3;
    border-radius: 4px;
    color: #ffffff;
    padding: 8px 14px;
}
QPushButton:hover:enabled {
    background: #417bb4;
}
QPushButton:disabled, QLineEdit:disabled {
    background: #292b30;
    border-color: #34363c;
    color: #777b85;
}
QListWidget {
    background: #24262b;
    border: none;
    color: #d8d8dc;
    outline: none;
    padding: 6px;
}
QListWidget::item {
    border-radius: 4px;
    margin: 2px 0;
    padding: 9px 8px;
}
QListWidget::item:hover {
    background: #30333a;
}
QListWidget::item:selected {
    background: #314d6b;
    color: #ffffff;
}
QSplitter::handle {
    background: #393c43;
    width: 1px;
}
QLabel#sectionTitle {
    color: #f0f1f3;
    font-size: 16px;
    font-weight: 600;
}
QLabel#noteTitle {
    color: #ffffff;
    font-size: 24px;
    font-weight: 600;
}
QLabel#metadata, QLabel#emptyHint {
    color: #9ca1ab;
}
"""
