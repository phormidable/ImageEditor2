#!/usr/bin/env python3
"""
Image Compositor - Main Application
Phase 1: Basic viewer with multiple image support
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QStatusBar, QToolBar, QVBoxLayout, QWidget, QLabel
)
from PySide6.QtGui import QAction, QKeySequence

from canvas_view import CanvasView


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("Image Compositor - Basic Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # Store current files
        self.loaded_files = []

        # Initialize UI
        self.init_ui()

        # Apply stylesheet
        self._apply_stylesheet()

    def init_ui(self):
        """Initialize the user interface"""

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create canvas
        self.canvas = CanvasView()
        layout.addWidget(self.canvas)

        # Connect signals
        self.canvas.image_added.connect(self.on_image_added)

        # Create menu bar
        self.create_menus()

        # Create toolbar
        self.create_toolbar()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add permanent widget to status bar to show image count
        self.image_count_label = QLabel("Images: 0")
        self.status_bar.addPermanentWidget(self.image_count_label)

        self.status_bar.showMessage("Ready - Drag and drop images or use File → Open")

        # Enable drag and drop on main window
        self.setAcceptDrops(True)

    def create_menus(self):
        """Create menu bar"""

        # File menu
        file_menu = self.menuBar().addMenu("&File")

        # Open action
        open_action = QAction("&Open Image...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        # Open Multiple action
        open_multiple_action = QAction("Open &Multiple Images...", self)
        open_multiple_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_multiple_action.triggered.connect(self.open_multiple_images)
        file_menu.addAction(open_multiple_action)

        file_menu.addSeparator()

        # Clear canvas action
        clear_action = QAction("&Clear Canvas", self)
        clear_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        clear_action.triggered.connect(self.clear_canvas)
        file_menu.addAction(clear_action)

        file_menu.addSeparator()

        # Export action (placeholder)
        export_action = QAction("&Export...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.setEnabled(False)  # Will enable in later phases
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = self.menuBar().addMenu("&View")

        # Zoom actions
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.canvas.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.canvas.zoom_out)
        view_menu.addAction(zoom_out_action)

        # Separate reset zoom and fit to window
        reset_zoom_action = QAction("Actual &Size (100%)", self)
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+1"))
        reset_zoom_action.triggered.connect(self.canvas.reset_zoom)
        view_menu.addAction(reset_zoom_action)

        fit_action = QAction("&Fit to Window", self)
        fit_action.setShortcut(QKeySequence("Ctrl+0"))
        fit_action.triggered.connect(self.canvas.fit_to_window)
        view_menu.addAction(fit_action)

        view_menu.addSeparator()

        # Show grid action (placeholder)
        show_grid_action = QAction("Show &Grid", self)
        show_grid_action.setCheckable(True)
        show_grid_action.setChecked(False)
        show_grid_action.setEnabled(False)  # For future
        view_menu.addAction(show_grid_action)

        # Help menu
        help_menu = self.menuBar().addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)

    def create_toolbar(self):
        """Create main toolbar"""

        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Open button
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_image)
        toolbar.addAction(open_action)

        # Open multiple button
        open_multiple_action = QAction("Open Multiple", self)
        open_multiple_action.triggered.connect(self.open_multiple_images)
        toolbar.addAction(open_multiple_action)

        toolbar.addSeparator()

        # Clear button
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.clear_canvas)
        toolbar.addAction(clear_action)

        toolbar.addSeparator()

        # Zoom controls
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.canvas.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.canvas.zoom_out)
        toolbar.addAction(zoom_out_action)

        reset_zoom_action = QAction("Actual Size", self)
        reset_zoom_action.triggered.connect(self.canvas.reset_zoom)
        toolbar.addAction(reset_zoom_action)

        fit_action = QAction("Fit to Window", self)
        fit_action.triggered.connect(self.canvas.fit_to_window)
        toolbar.addAction(fit_action)

    def open_image(self):
        """Open single image file dialog"""

        filepath = self._get_image_filepath()
        if filepath:
            success = self.canvas.load_image(filepath)
            if success:
                self.loaded_files.append(Path(filepath))
                self.update_window_title()

    def open_multiple_images(self):
        """Open multiple image files at once"""

        filepaths = self._get_multiple_image_filepaths()
        if filepaths:
            for filepath in filepaths:
                success = self.canvas.load_image(filepath)
                if success:
                    self.loaded_files.append(Path(filepath))

            self.update_window_title()

    def _get_image_filepath(self):
        """Open file dialog for single image"""
        formats = [
            "*.png", "*.jpg", "*.jpeg", "*.bmp",
            "*.gif", "*.tif", "*.tiff", "*.webp"
        ]
        filter_str = f"Images ({' '.join(formats)})"

        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", filter_str
        )

        return filepath if filepath else None

    def _get_multiple_image_filepaths(self):
        """Open file dialog for multiple images"""
        formats = [
            "*.png", "*.jpg", "*.jpeg", "*.bmp",
            "*.gif", "*.tif", "*.tiff", "*.webp"
        ]
        filter_str = f"Images ({' '.join(formats)})"

        filepaths, _ = QFileDialog.getOpenFileNames(
            self, "Open Multiple Images", "", filter_str
        )

        return filepaths if filepaths else []

    def clear_canvas(self):
        """Clear all images from canvas"""
        if self.canvas.get_image_count() > 0:
            reply = QMessageBox.question(
                self, "Clear Canvas",
                "Are you sure you want to clear all images from the canvas?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.canvas.clear_all()
                self.loaded_files.clear()
                self.update_window_title()
                self.status_bar.showMessage("Canvas cleared", 3000)

    def update_window_title(self):
        """Update window title based on loaded images"""
        count = self.canvas.get_image_count()

        if count == 0:
            self.setWindowTitle("Image Compositor - Basic Viewer")
        elif count == 1 and self.loaded_files:
            self.setWindowTitle(f"Image Compositor - {self.loaded_files[-1].name}")
        else:
            self.setWindowTitle(f"Image Compositor - {count} images")

    def on_image_added(self, filename: str, image_rect, position):
        """Handle image added signal"""
        # Update image count in status bar
        count = self.canvas.get_image_count()
        self.image_count_label.setText(f"Images: {count}")

        # Show image info in status bar temporarily
        from pathlib import Path
        img_name = Path(filename).name
        self.status_bar.showMessage(
            f"Loaded: {img_name} ({image_rect.width():.0f}×{image_rect.height():.0f})",
            3000
        )

    # Drag and drop support for main window
    def dragEnterEvent(self, event):
        """Handle drag enter event for file drops"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event for file drops"""
        if event.mimeData().hasUrls():
            # Forward to canvas for handling
            self.canvas.dropEvent(event)
            event.acceptProposedAction()

    def show_about(self):
        """Show about dialog"""
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

        QMessageBox.about(self, "About Image Compositor", about_text)

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_text = """
        <h3>Keyboard Shortcuts</h3>
        <table>
        <tr><td><b>Ctrl+O</b></td><td>Open image</td></tr>
        <tr><td><b>Ctrl+Shift+O</b></td><td>Open multiple images</td></tr>
        <tr><td><b>Ctrl+Shift+C</b></td><td>Clear canvas</td></tr>
        <tr><td><b>Ctrl+E</b></td><td>Export (coming soon)</td></tr>
        <tr><td><b>Ctrl++</b></td><td>Zoom in</td></tr>
        <tr><td><b>Ctrl+-</b></td><td>Zoom out</td></tr>
        <tr><td><b>Ctrl+0</b></td><td>Fit to window</td></tr>
        <tr><td><b>Ctrl+1</b></td><td>Actual size (100%)</td></tr>
        <tr><td><b>Ctrl+Wheel</b></td><td>Zoom in/out at mouse position</td></tr>
        </table>
        """

        QMessageBox.about(self, "Keyboard Shortcuts", shortcuts_text)

    def _apply_stylesheet(self):
        """Apply a basic stylesheet for better appearance"""
        self.setStyleSheet("""
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
        """)


def main():
    """Application entry point"""

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Image Compositor")
    app.setOrganizationName("MyOrg")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Handle command line arguments
    if len(sys.argv) > 1:
        # Load all provided image files
        for arg in sys.argv[1:]:
            if Path(arg).exists():
                window.canvas.load_image(arg)

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()