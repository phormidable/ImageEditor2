from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtGui import QPainter, QPixmap, QBrush, QColor
from PySide6.QtCore import Qt, QRectF, Signal, QPointF


class CanvasView(QGraphicsView):
    """Custom graphics view for the canvas with zoom and multiple image support"""

    # Signal emitted when an image is loaded
    image_loaded = Signal(str, QRectF)  # filename, image_rect
    image_added = Signal(str, QRectF, QPointF)  # filename, image_rect, position

    def __init__(self):
        super().__init__()

        # Create scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Set up rendering
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Enable mouse tracking for future features
        self.setMouseTracking(True)

        # Store all image items
        self.image_items = []

        # Zoom properties
        self.zoom_factor = 1.25
        self.current_zoom = 1.0
        self.min_zoom = 0.01
        self.max_zoom = 100.0

        # Track actual size (100% zoom)
        self.actual_size_zoom = 1.0

        # Set background
        self.setBackgroundBrush(self._create_background_pattern())

        # Store the welcome text item for easy removal
        self.welcome_text_item = None
        self._add_welcome_message()

        # Setup scene size
        self.setSceneRect(-500, -500, 1000, 1000)

    def _create_background_pattern(self):
        """Create a checkerboard pattern for transparent background visualization"""
        from PySide6.QtGui import QPixmap

        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
        painter.fillRect(0, 0, 32, 32, QColor(220, 220, 220))
        painter.fillRect(32, 32, 32, 32, QColor(220, 220, 220))
        painter.end()

        return QBrush(pixmap)

    def _add_welcome_message(self):
        """Add initial welcome text to the canvas"""
        if self.welcome_text_item:
            self.scene.removeItem(self.welcome_text_item)

        welcome_text = "Drag and drop images here\nor use File → Open"
        self.welcome_text_item = self.scene.addText(welcome_text)
        self.welcome_text_item.setDefaultTextColor(Qt.darkGray)

        # Center the text
        text_rect = self.welcome_text_item.boundingRect()
        self.welcome_text_item.setPos(-text_rect.width() / 2, -text_rect.height() / 2)

    def _remove_welcome_message(self):
        """Remove the welcome message when images are added"""
        if self.welcome_text_item:
            self.scene.removeItem(self.welcome_text_item)
            self.welcome_text_item = None

    def load_image(self, filepath, position=None):
        """Load an image file into the canvas at specified position"""
        try:
            # Load pixmap
            pixmap = QPixmap(filepath)

            if pixmap.isNull():
                return False

            # Create graphics item
            image_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(image_item)

            # Set position (center if not specified)
            if position is None:
                # Calculate center of visible area
                view_center = self.mapToScene(self.viewport().rect().center())
                img_rect = image_item.boundingRect()
                position = view_center - QPointF(img_rect.width() / 2, img_rect.height() / 2)

            image_item.setPos(position)

            # Make image movable and selectable (for future features)
            image_item.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
            image_item.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)

            # Store the item
            self.image_items.append(image_item)

            # Remove welcome message if this is the first image
            if len(self.image_items) == 1:
                self._remove_welcome_message()

            # Update scene bounds to include all images
            self._update_scene_bounds()

            # Fit view to all images on first load
            if len(self.image_items) == 1:
                self.fit_to_window()

            # Emit signal with image info
            img_rect = image_item.boundingRect()
            self.image_added.emit(filepath, img_rect, position)

            return True

        except Exception as e:
            print(f"Failed to load image: {str(e)}")
            return False

    def _update_scene_bounds(self):
        """Update scene rectangle to include all items"""
        if not self.image_items:
            return

        # Start with first item's bounds
        first_item = self.image_items[0]
        bounds = first_item.sceneBoundingRect()

        # Expand to include all items
        for item in self.image_items[1:]:
            bounds = bounds.united(item.sceneBoundingRect())

        # Add some padding
        bounds.adjust(-50, -50, 50, 50)
        self.scene.setSceneRect(bounds)

    def wheelEvent(self, event):
        """Handle zoom with mouse wheel and Ctrl key"""
        if event.modifiers() & Qt.ControlModifier:
            # Zoom in/out with Ctrl + Wheel
            zoom_in = event.angleDelta().y() > 0

            old_pos = self.mapToScene(event.position().toPoint())

            if zoom_in and self.current_zoom < self.max_zoom:
                self.scale(self.zoom_factor, self.zoom_factor)
                self.current_zoom *= self.zoom_factor
            elif not zoom_in and self.current_zoom > self.min_zoom:
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
                self.current_zoom /= self.zoom_factor

            # Center on mouse position
            new_pos = self.mapToScene(event.position().toPoint())
            delta = new_pos - old_pos
            self.translate(delta.x(), delta.y())

            event.accept()
        else:
            # Default behavior (scroll)
            super().wheelEvent(event)

    def reset_zoom(self):
        """Reset zoom to actual size (100%)"""
        if not self.image_items:
            return

        # Calculate the scale needed to return to actual size
        current_transform = self.transform()
        scale_x = current_transform.m11()  # Get current scale factor

        if scale_x != 0:
            # Reset to actual size
            self.resetTransform()
            self.current_zoom = 1.0

            # Center on the scene
            self.centerOn(self.scene.itemsBoundingRect().center())

    def fit_to_window(self):
        """Fit all content to the viewport"""
        if not self.image_items:
            return

        # Fit the view to all items
        bounds = self.scene.itemsBoundingRect()
        if bounds.isValid():
            self.fitInView(bounds, Qt.KeepAspectRatio)

            # Calculate current zoom level after fitting
            view_width = self.viewport().width()
            scene_width = bounds.width()
            if scene_width > 0:
                self.current_zoom = view_width / scene_width * 0.9  # Add some padding

    def zoom_in(self):
        """Zoom in by zoom factor"""
        if self.current_zoom < self.max_zoom:
            self.scale(self.zoom_factor, self.zoom_factor)
            self.current_zoom *= self.zoom_factor

    def zoom_out(self):
        """Zoom out by zoom factor"""
        if self.current_zoom > self.min_zoom:
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
            self.current_zoom /= self.zoom_factor

    def clear_all(self):
        """Clear all images from canvas"""
        for item in self.image_items:
            self.scene.removeItem(item)
        self.image_items.clear()
        self._add_welcome_message()
        self.current_zoom = 1.0
        self.resetTransform()

    def get_image_count(self):
        """Return number of images on canvas"""
        return len(self.image_items)

    # Drag and drop support
    def dragEnterEvent(self, event):
        """Handle drag enter event for file drops"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        """Handle drag move event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        """Handle drop event for file drops"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()

            # Get drop position
            drop_pos = self.mapToScene(event.position().toPoint())

            # Load each dropped image
            for url in urls:
                filepath = url.toLocalFile()

                # Check if it's an image file
                if any(filepath.lower().endswith(ext) for ext in
                       ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif', '.tiff', '.webp']):
                    self.load_image(filepath, drop_pos)
                    # Offset next image slightly
                    drop_pos += QPointF(20, 20)

            event.acceptProposedAction()
        else:
            super().dropEvent(event)