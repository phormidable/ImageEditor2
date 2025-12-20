"""
Helper functions, constants, and utilities for the Image Compositor app.
"""

from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt

# Image formats supported
IMAGE_FORMATS = [
    "*.png", "*.jpg", "*.jpeg", "*.bmp",
    "*.gif", "*.tif", "*.tiff", "*.webp"
]

def get_image_filter_string() -> str:
    """Return filter string for QFileDialog."""
    return f"Images ({' '.join(IMAGE_FORMATS)})"


def is_image_file(filepath: str) -> bool:
    """Check if a file is an image based on extension."""
    if not filepath:
        return False
    return any(filepath.lower().endswith(ext[1:]) for ext in IMAGE_FORMATS)


def create_checkerboard_brush() -> "QBrush":
    """Create a checkerboard pattern brush for transparent backgrounds."""
    from PySide6.QtGui import QBrush

    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.white)

    painter = QPainter(pixmap)
    painter.fillRect(0, 0, 32, 32, QColor(220, 220, 220))
    painter.fillRect(32, 32, 32, 32, QColor(220, 220, 220))
    painter.end()

    return QBrush(pixmap)


def show_about_dialog(parent) -> None:
    """Show the about dialog."""
    about_text = """
    <h2>Image Compositor</h2>
    <p>Image viewer and compositor tool with multiple image support.</p>
    <p>Version 0.1.1 (Phase 1 - Multiple Images)</p>
    <p>Built with PySide6</p>
    <p><b>Features:</b></p>
    <ul>
        <li>Open single or multiple images</li>
        <li>Drag and drop support</li>
        <li>Zoom with Ctrl+Mouse Wheel or buttons</li>
        <li>Actual size (100%) and fit to window</li>
        <li>Multiple images on canvas</li>
    </ul>
    <p>Use <b>Ctrl+0</b> to fit to window, <b>Ctrl+1</b> for actual size.</p>
    """

    QMessageBox.about(parent, "About Image Compositor", about_text)


def show_shortcuts_dialog(parent) -> None:
    """Show keyboard shortcuts dialog."""
    shortcuts_text = """
    <h3>Keyboard Shortcuts</h3>
    <table>
    <tr><td><b>Ctrl+O</b></td><td>Open image</td></tr>
    <tr><td><b>Ctrl+Shift+O</b></td><td>Open multiple images</td></tr>
    <tr><td><b>Ctrl+Shift+C</b></td><td>Clear canvas</td></tr>
    <tr><td><b>Delete</b></td><td>Delete selected image(s)</td></tr>
    <tr><td><b>Ctrl+Shift+D</b></td><td>Delete all images</td></tr>
    <tr><td><b>Ctrl+Shift+F</b></td><td>Bring to front</td></tr>
    <tr><td><b>Ctrl+Shift+B</b></td><td>Send to back</td></tr>
    <tr><td><b>Ctrl+E</b></td><td>Export (coming soon)</td></tr>
    <tr><td><b>Ctrl++</b></td><td>Zoom in</td></tr>
    <tr><td><b>Ctrl+-</b></td><td>Zoom out</td></tr>
    <tr><td><b>Ctrl+0</b></td><td>Fit to window</td></tr>
    <tr><td><b>Ctrl+1</b></td><td>Actual size (100%)</td></tr>
    <tr><td><b>Ctrl+Wheel</b></td><td>Zoom in/out at mouse position</td></tr>
    </table>
    """

    QMessageBox.about(parent, "Keyboard Shortcuts", shortcuts_text)


def get_stylesheet() -> str:
    """Return the application stylesheet."""
    return """
    QMainWindow {
        background-color: #2b2b2b;
    }
    QToolBar {
        background-color: #3c3c3c;
        border: none;
        padding: 2px;
    }
    QToolButton {
        color: #ffffff;
        background-color: #3c3c3c;
        border: 1px solid #3c3c3c;
        border-radius: 3px;
        padding: 5px;
        margin: 1px;
    }
    QToolButton:hover {
        background-color: #505050;
        border: 1px solid #505050;
    }
    QToolButton:pressed {
        background-color: #1e1e1e;
    }
    QToolButton:checked {
        background-color: #1e6ae1;
        border: 1px solid #1e6ae1;
    }
    QStatusBar {
        color: #cccccc;
        background-color: #2b2b2b;
        border-top: 1px solid #3c3c3c;
    }
    QMenuBar {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QMenuBar::item:selected {
        background-color: #505050;
    }
    QMenu {
        background-color: #3c3c3c;
        color: #ffffff;
    }
    QMenu::item:selected {
        background-color: #505050;
    }
    """