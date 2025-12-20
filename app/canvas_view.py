"""
Canvas view for displaying and manipulating images.
"""

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt, QRectF, Signal, QPointF

from .helpers import create_checkerboard_brush, is_image_file


class ImageItem(QGraphicsPixmapItem):
    """Custom image item that stores the filepath."""
    def __init__(self, pixmap, filepath=""):
        super().__init__(pixmap)
        self.filepath = filepath


class CanvasView(QGraphicsView):
    """Custom graphics view for the canvas with zoom and multiple image support."""

    # Signals
    image_added = Signal(str, QRectF, QPointF)  # filename, image_rect, position
    image_removed = Signal(str)  # filename of removed image

    # Constants
    ZOOM_FACTOR = 1.25
    MIN_ZOOM = 0.01
    MAX_ZOOM = 100.0
    SCENE_PADDING = 50
    IMAGE_OFFSET = QPointF(20, 20)

    def __init__(self):
        super().__init__()
        self._setup_view()
        self._setup_scene()
        self._setup_properties()

    def _setup_view(self):
        """Configure the view settings."""
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setBackgroundBrush(create_checkerboard_brush())

    def _setup_scene(self):
        """Initialize the scene."""
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(-500, -500, 1000, 1000)
        self._add_welcome_message()

    def _setup_properties(self):
        """Initialize instance properties."""
        self.image_items = []
        self.current_zoom = 1.0
        self.welcome_text_item = None

    def _add_welcome_message(self):
        """Add initial welcome text to the canvas."""
        welcome_text = "Drag and drop images here\nor use File → Open"
        self.welcome_text_item = self.scene.addText(welcome_text)
        self.welcome_text_item.setDefaultTextColor(Qt.darkGray)

        # Center the text
        text_rect = self.welcome_text_item.boundingRect()
        self.welcome_text_item.setPos(-text_rect.width() / 2, -text_rect.height() / 2)

    def _remove_welcome_message(self):
        """Remove the welcome message when images are added."""
        if self.welcome_text_item:
            self.scene.removeItem(self.welcome_text_item)
            self.welcome_text_item = None

    def load_image(self, filepath: str, position: QPointF = None) -> bool:
        """Load an image file into the canvas at specified position."""
        try:
            pixmap = QPixmap(filepath)
            if pixmap.isNull():
                return False

            # Create and position the image item
            image_item = self._create_image_item(pixmap, filepath, position)
            self.scene.addItem(image_item)
            self.image_items.append(image_item)

            # Update UI state
            self._on_image_added()

            # Emit signal
            img_rect = image_item.boundingRect()
            self.image_added.emit(filepath, img_rect, image_item.pos())

            return True

        except Exception as e:
            print(f"Failed to load image: {str(e)}")
            return False

    def _create_image_item(self, pixmap: QPixmap, filepath: str,
                          position: QPointF = None) -> ImageItem:
        """Create a custom ImageItem with proper settings."""
        image_item = ImageItem(pixmap, filepath)

        # Set position
        if position is None:
            position = self._calculate_center_position(image_item)
        image_item.setPos(position)

        # Enable interaction
        image_item.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        image_item.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)

        return image_item

    def _calculate_center_position(self, image_item: ImageItem) -> QPointF:
        """Calculate position to center image in view."""
        view_center = self.mapToScene(self.viewport().rect().center())
        img_rect = image_item.boundingRect()
        return view_center - QPointF(img_rect.width() / 2, img_rect.height() / 2)

    def _on_image_added(self):
        """Handle actions after an image is added."""
        if len(self.image_items) == 1:
            self._remove_welcome_message()

        self._update_scene_bounds()

        if len(self.image_items) == 1:
            self.fit_to_window()

    def _update_scene_bounds(self):
        """Update scene rectangle to include all items."""
        if not self.image_items:
            return

        bounds = self.image_items[0].sceneBoundingRect()
        for item in self.image_items[1:]:
            bounds = bounds.united(item.sceneBoundingRect())

        bounds.adjust(-self.SCENE_PADDING, -self.SCENE_PADDING,
                      self.SCENE_PADDING, self.SCENE_PADDING)
        self.scene.setSceneRect(bounds)

    def wheelEvent(self, event):
        """Handle zoom with mouse wheel and Ctrl key."""
        if event.modifiers() & Qt.ControlModifier:
            self._handle_zoom(event)
            event.accept()
        else:
            super().wheelEvent(event)

    def _handle_zoom(self, event):
        """Handle zooming at mouse position."""
        zoom_in = event.angleDelta().y() > 0
        old_pos = self.mapToScene(event.position().toPoint())

        if zoom_in and self.current_zoom < self.MAX_ZOOM:
            self.scale(self.ZOOM_FACTOR, self.ZOOM_FACTOR)
            self.current_zoom *= self.ZOOM_FACTOR
        elif not zoom_in and self.current_zoom > self.MIN_ZOOM:
            self.scale(1 / self.ZOOM_FACTOR, 1 / self.ZOOM_FACTOR)
            self.current_zoom /= self.ZOOM_FACTOR

        # Maintain mouse position
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def reset_zoom(self):
        """Reset zoom to actual size (100%)."""
        if not self.image_items:
            return

        self.resetTransform()
        self.current_zoom = 1.0
        self.centerOn(self.scene.itemsBoundingRect().center())

    def fit_to_window(self):
        """Fit all content to the viewport."""
        if not self.image_items:
            return

        bounds = self.scene.itemsBoundingRect()
        if bounds.isValid():
            self.fitInView(bounds, Qt.KeepAspectRatio)

            # Calculate current zoom level after fitting
            view_width = self.viewport().width()
            scene_width = bounds.width()
            if scene_width > 0:
                self.current_zoom = view_width / scene_width * 0.9

    def zoom_in(self):
        """Zoom in by zoom factor."""
        if self.current_zoom < self.MAX_ZOOM:
            self.scale(self.ZOOM_FACTOR, self.ZOOM_FACTOR)
            self.current_zoom *= self.ZOOM_FACTOR

    def zoom_out(self):
        """Zoom out by zoom factor."""
        if self.current_zoom > self.MIN_ZOOM:
            self.scale(1 / self.ZOOM_FACTOR, 1 / self.ZOOM_FACTOR)
            self.current_zoom /= self.ZOOM_FACTOR

    def delete_selected(self):
        """Delete all selected image items."""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return

        # Remove selected items
        for item in selected_items:
            if item in self.image_items:
                # Emit signal before removal
                if hasattr(item, 'filepath'):
                    self.image_removed.emit(item.filepath)

                # Remove from scene and tracking list
                self.scene.removeItem(item)
                self.image_items.remove(item)

        # Update UI state
        if not self.image_items:
            self._add_welcome_message()

        self._update_scene_bounds()

    def clear_all(self):
        """Clear all images from canvas."""
        for item in self.image_items:
            # Emit removal signals
            if hasattr(item, 'filepath'):
                self.image_removed.emit(item.filepath)
            self.scene.removeItem(item)

        self.image_items.clear()
        self._add_welcome_message()
        self.current_zoom = 1.0
        self.resetTransform()

    def get_image_count(self) -> int:
        """Return number of images on canvas."""
        return len(self.image_items)

    def get_selected_count(self) -> int:
        """Return number of selected images."""
        return len(self.scene.selectedItems())

    # Drag and drop support
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            drop_pos = self.mapToScene(event.position().toPoint())

            for url in urls:
                filepath = url.toLocalFile()
                if is_image_file(filepath):
                    self.load_image(filepath, drop_pos)
                    drop_pos += self.IMAGE_OFFSET

            event.acceptProposedAction()
        else:
            super().dropEvent(event)