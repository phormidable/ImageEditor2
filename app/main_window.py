"""
Main application window for Image Compositor.
"""

from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QStatusBar, QToolBar, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt

from .canvas_view import CanvasView
from .helpers import get_image_filter_string, show_about_dialog, show_shortcuts_dialog, get_stylesheet

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.loaded_files = []
        self._setup_window()
        self._init_ui()
        self._apply_stylesheet()

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Image Compositor - Basic Viewer")
        self.setGeometry(100, 100, 1200, 800)
        self.setAcceptDrops(True)

    def _init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create canvas
        self.canvas = CanvasView()
        layout.addWidget(self.canvas)

        # Connect signals
        self.canvas.image_added.connect(self._on_image_added)
        self.canvas.image_removed.connect(self._on_image_removed)

        # Create UI components
        self._create_menus()
        self._create_toolbar()
        self._create_status_bar()

    def _create_menus(self):
        """Create menu bar."""

        # File menu
        file_menu = self.menuBar().addMenu("&File")
        self._add_file_menu_actions(file_menu)

        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        self._add_edit_menu_actions(edit_menu)

        # View menu
        view_menu = self.menuBar().addMenu("&View")
        self._add_view_menu_actions(view_menu)

        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        self._add_help_menu_actions(help_menu)

    def _add_file_menu_actions(self, menu):
        """Add actions to File menu."""
        actions = [
            ("&Open Image...", QKeySequence.Open, self.open_image, None),
            ("Open &Multiple Images...", "Ctrl+Shift+O", self.open_multiple_images, None),
            (None, None, None, None),  # Separator
            ("&Clear Canvas", "Ctrl+Shift+C", self.clear_canvas, None),
            (None, None, None, None),  # Separator
            ("&Export...", "Ctrl+E", None, False),  # Disabled for now
            (None, None, None, None),  # Separator
            ("E&xit", QKeySequence.Quit, self.close, None)
        ]

        for label, shortcut, handler, enabled in actions:
            if label is None:
                menu.addSeparator()
            else:
                action = QAction(label, self)
                if shortcut:
                    action.setShortcut(shortcut)
                if handler:
                    action.triggered.connect(handler)
                if enabled is not None:
                    action.setEnabled(enabled)
                menu.addAction(action)

    def _add_edit_menu_actions(self, menu):
        """Add actions to Edit menu."""
        actions = [
            ("&Delete Selection", QKeySequence.Delete, self.delete_selection, None),
            ("Delete All Images", "Ctrl+Shift+D", self.clear_canvas, None),
        ]

        for label, shortcut, handler, enabled in actions:
            action = QAction(label, self)
            if shortcut:
                action.setShortcut(shortcut)
            if handler:
                action.triggered.connect(handler)
            if enabled is not None:
                action.setEnabled(enabled)
            menu.addAction(action)

    def _add_view_menu_actions(self, menu):
        """Add actions to View menu."""
        zoom_actions = [
            ("Zoom &In", QKeySequence.ZoomIn, self.canvas.zoom_in),
            ("Zoom &Out", QKeySequence.ZoomOut, self.canvas.zoom_out),
            ("Actual &Size (100%)", "Ctrl+1", self.canvas.reset_zoom),
            ("&Fit to Window", "Ctrl+0", self.canvas.fit_to_window)
        ]

        for label, shortcut, handler in zoom_actions:
            action = QAction(label, self)
            action.setShortcut(shortcut)
            action.triggered.connect(handler)
            menu.addAction(action)

        menu.addSeparator()

        # Placeholder for future features
        show_grid = QAction("Show &Grid", self)
        show_grid.setCheckable(True)
        show_grid.setChecked(False)
        show_grid.setEnabled(False)
        menu.addAction(show_grid)

    def _add_help_menu_actions(self, menu):
        """Add actions to Help menu."""
        actions = [
            ("&About", show_about_dialog),
            ("&Keyboard Shortcuts", show_shortcuts_dialog)
        ]

        for label, handler in actions:
            action = QAction(label, self)
            action.triggered.connect(lambda checked, h=handler: h(self))
            menu.addAction(action)

    def _create_toolbar(self):
        """Create main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Toolbar actions
        toolbar_actions = [
            ("Open", self.open_image),
            ("Open Multiple", self.open_multiple_images),
            (None, None),  # Separator
            ("Delete", self.delete_selection),
            ("Clear All", self.clear_canvas),
            (None, None),  # Separator
            ("Zoom In", self.canvas.zoom_in),
            ("Zoom Out", self.canvas.zoom_out),
            ("Actual Size", self.canvas.reset_zoom),
            ("Fit to Window", self.canvas.fit_to_window)
        ]

        for label, handler in toolbar_actions:
            if label is None:
                toolbar.addSeparator()
            else:
                action = QAction(label, self)
                action.triggered.connect(handler)
                toolbar.addAction(action)

    def _create_status_bar(self):
        """Create and configure status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Image count label
        self.image_count_label = QLabel("Images: 0")
        self.status_bar.addPermanentWidget(self.image_count_label)

        # Selected count label
        self.selected_count_label = QLabel("Selected: 0")
        self.status_bar.addPermanentWidget(self.selected_count_label)

        self.status_bar.showMessage("Ready - Drag and drop images or use File → Open")

    def open_image(self):
        """Open single image file dialog."""
        filepath = self._get_filepath_single()
        if filepath:
            self._load_image_file(filepath)

    def open_multiple_images(self):
        """Open multiple image files at once."""
        filepaths = self._get_filepaths_multiple()
        if filepaths:
            for filepath in filepaths:
                self._load_image_file(filepath)

    def _get_filepath_single(self) -> str:
        """Get single file path from dialog."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", get_image_filter_string()
        )
        return filepath if filepath else None

    def _get_filepaths_multiple(self) -> list:
        """Get multiple file paths from dialog."""
        filepaths, _ = QFileDialog.getOpenFileNames(
            self, "Open Multiple Images", "", get_image_filter_string()
        )
        return filepaths if filepaths else []

    def _load_image_file(self, filepath: str):
        """Load an image file and update UI."""
        success = self.canvas.load_image(filepath)
        if success:
            self.loaded_files.append(Path(filepath))
            self._update_window_title()

    def delete_selection(self):
        """Delete selected image(s)."""
        selected_count = self.canvas.get_selected_count()
        if selected_count == 0:
            QMessageBox.information(self, "No Selection",
                                   "No images are selected. Select an image by clicking on it.")
            return

        # Confirm deletion
        if selected_count == 1:
            message = "Delete the selected image?"
        else:
            message = f"Delete {selected_count} selected images?"

        reply = QMessageBox.question(
            self, "Delete Selection", message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.canvas.delete_selected()
            self._update_selection_count()
            self.status_bar.showMessage(f"Deleted {selected_count} image(s)", 3000)

    def clear_canvas(self):
        """Clear all images from canvas."""
        if self.canvas.get_image_count() == 0:
            return

        reply = QMessageBox.question(
            self, "Clear Canvas",
            "Are you sure you want to clear all images from the canvas?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.canvas.clear_all()
            self.loaded_files.clear()
            self._update_window_title()
            self._update_selection_count()
            self.status_bar.showMessage("Canvas cleared", 3000)

    def _update_window_title(self):
        """Update window title based on loaded images."""
        count = self.canvas.get_image_count()

        if count == 0:
            self.setWindowTitle("Image Compositor - Basic Viewer")
        elif count == 1 and self.loaded_files:
            self.setWindowTitle(f"Image Compositor - {self.loaded_files[-1].name}")
        else:
            self.setWindowTitle(f"Image Compositor - {count} images")

    def _on_image_added(self, filename: str, image_rect, position):
        """Handle image added signal."""
        # Update image count
        count = self.canvas.get_image_count()
        self.image_count_label.setText(f"Images: {count}")

        # Show temporary message
        img_name = Path(filename).name
        self.status_bar.showMessage(
            f"Loaded: {img_name} ({image_rect.width():.0f}×{image_rect.height():.0f})",
            3000
        )

    def _on_image_removed(self, filepath: str):
        """Handle image removed signal."""
        # Remove from loaded files list
        path = Path(filepath)
        if path in self.loaded_files:
            self.loaded_files.remove(path)

        # Update image count
        count = self.canvas.get_image_count()
        self.image_count_label.setText(f"Images: {count}")
        self._update_window_title()

    def _update_selection_count(self):
        """Update the selected count in status bar."""
        selected_count = self.canvas.get_selected_count()
        self.selected_count_label.setText(f"Selected: {selected_count}")

    # Event handlers for selection changes
    def mousePressEvent(self, event):
        """Update selection count when clicking."""
        super().mousePressEvent(event)
        # Small delay to allow selection to update
        from PySide6.QtCore import QTimer
        QTimer.singleShot(10, self._update_selection_count)

    def keyPressEvent(self, event):
        """Handle key presses for delete."""
        if event.key() == Qt.Key_Delete:
            self.delete_selection()
        else:
            super().keyPressEvent(event)

    # Drag and drop support
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            self.canvas.dropEvent(event)
            event.acceptProposedAction()

    def _apply_stylesheet(self):
        """Apply the application stylesheet."""
        self.setStyleSheet(get_stylesheet())