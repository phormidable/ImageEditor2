"""
Main application window for Image Compositor - UI definition only.
"""

from PySide6.QtWidgets import QMainWindow, QStatusBar, QToolBar, QVBoxLayout, QWidget, QLabel, QGraphicsView
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt

from .canvas_view import CanvasView
from .main_window_toolbox import MainWindowToolbox
from .helpers import show_about_dialog, show_shortcuts_dialog, get_stylesheet


class MainWindow(QMainWindow):
    """Main application window - UI definition only."""

    def __init__(self):
        super().__init__()
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
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create canvas, then the toolbox
        self.canvas = CanvasView()
        layout.addWidget(self.canvas)
        self.toolbox = MainWindowToolbox(self)

        # Update toolbox reference now that canvas exists
        self.toolbox.canvas = self.canvas

        # Connect canvas signals to toolbox methods
        self.canvas.image_added.connect(self.toolbox.on_image_added)
        self.canvas.image_removed.connect(self.toolbox.on_image_removed)

        # Connect mouse events for crop mode
        self.canvas.mousePressEvent = self._handle_canvas_mouse_press
        self.canvas.mouseMoveEvent = self._handle_canvas_mouse_move
        self.canvas.mouseReleaseEvent = self._handle_canvas_mouse_release

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
            ("&Open Image...", QKeySequence.Open, self.toolbox.open_image),
            ("Open &Multiple Images...", "Ctrl+Shift+O", self.toolbox.open_multiple_images),
            (None, None, None),  # Separator
            ("&Clear Canvas", "Ctrl+Shift+C", self.toolbox.clear_canvas),
            (None, None, None),  # Separator
            ("&Export...", "Ctrl+E", None, False),  # Disabled for now
            (None, None, None),  # Separator
            ("E&xit", QKeySequence.Quit, self.close)
        ]

        for label, shortcut, handler, *enabled in actions:
            if label is None:
                menu.addSeparator()
            else:
                action = QAction(label, self)
                if shortcut:
                    action.setShortcut(shortcut)
                if handler:
                    action.triggered.connect(handler)
                if enabled:
                    action.setEnabled(enabled[0])
                menu.addAction(action)

    def _add_edit_menu_actions(self, menu):
        """Add actions to Edit menu."""
        actions = [
            ("&Delete Selection", QKeySequence.Delete, self.toolbox.delete_selection),
            ("Delete All Images", "Ctrl+Shift+D", self.toolbox.clear_canvas),
            (None, None, None),  # Separator
            ("Bring to &Front", "Ctrl+Shift+F", self.toolbox.move_to_front),
            ("Send to &Back", "Ctrl+Shift+B", self.toolbox.move_to_back),
            (None, None, None),  # Separator
            ("&Crop Mode", "Ctrl+R", self.toolbox.toggle_crop_mode),  # NEW: Crop mode
            ("Crop to New &Image", "Ctrl+K", self.toolbox.crop_to_new_image),
        ]

        for label, shortcut, handler in actions:
            if label is None:
                menu.addSeparator()
            else:
                action = QAction(label, self)
                if shortcut:
                    action.setShortcut(shortcut)
                if handler:
                    action.triggered.connect(handler)
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
            ("Open", self.toolbox.open_image),
            ("Open Multiple", self.toolbox.open_multiple_images),
            (None, None),  # Separator
            ("Delete", self.toolbox.delete_selection),
            ("Clear All", self.toolbox.clear_canvas),
            (None, None),  # Separator
            ("Bring to Front", self.toolbox.move_to_front),
            ("Send to Back", self.toolbox.move_to_back),
            (None, None),  # Separator
            ("Crop", self.toolbox.toggle_crop_mode),  # NEW: Crop button
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

                # Make crop button checkable to show mode state
                if label == "Crop":
                    action.setCheckable(True)
                    action.toggled.connect(self._on_crop_toggled)

                toolbar.addAction(action)

            # Store reference to crop action for updating
        self.crop_action = toolbar.actions()[toolbar_actions.index(("Crop", self.toolbox.toggle_crop_mode))]

    def _on_crop_toggled(self, checked):
        """Handle crop button toggle."""
        # Update button appearance
        if checked:
            self.crop_action.setText("Crop (ON)")
        else:
            self.crop_action.setText("Crop")

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

    # UI update methods (called by toolbox)
    def update_window_title(self):
        """Update window title based on loaded images."""
        count = self.canvas.get_image_count()

        if count == 0:
            self.setWindowTitle("Image Compositor - Basic Viewer")
        elif count == 1 and self.toolbox.loaded_files:
            self.setWindowTitle(f"Image Compositor - {self.toolbox.loaded_files[-1].name}")
        else:
            self.setWindowTitle(f"Image Compositor - {count} images")

    def update_selection_count(self):
        """Update the selected count in status bar."""
        selected_count = self.canvas.get_selected_count()
        self.selected_count_label.setText(f"Selected: {selected_count}")

    # Event handlers
    def keyPressEvent(self, event):
        """Handle key presses for delete."""
        if event.key() == Qt.Key_Delete:
            self.toolbox.delete_selection()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Update selection count when clicking."""
        super().mousePressEvent(event)
        # Small delay to allow selection to update
        from PySide6.QtCore import QTimer
        QTimer.singleShot(10, self.update_selection_count)

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

    def _handle_canvas_mouse_press(self, event):
        """Handle mouse press on canvas."""
        if self.toolbox.crop_mode:
            self.toolbox.handle_crop_mouse_press(event)
        else:
            # Call original canvas mouse press event
            QGraphicsView.mousePressEvent(self.canvas, event)

        # Update selection count
        self.update_selection_count()

    def _handle_canvas_mouse_move(self, event):
        """Handle mouse move on canvas."""
        if self.toolbox.crop_mode:
            self.toolbox.handle_crop_mouse_move(event)
        else:
            # Call original canvas mouse move event
            QGraphicsView.mouseMoveEvent(self.canvas, event)

    def _handle_canvas_mouse_release(self, event):
        """Handle mouse release on canvas."""
        if self.toolbox.crop_mode:
            self.toolbox.handle_crop_mouse_release(event)
        else:
            # Call original canvas mouse release event
            QGraphicsView.mouseReleaseEvent(self.canvas, event)