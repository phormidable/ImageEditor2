"""
Toolbox containing business logic for MainWindow.
"""

from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QColor

from .helpers import get_image_filter_string

class MainWindowToolbox:
    """Contains business logic methods for MainWindow."""

    def __init__(self, main_window):
        self.main_window = main_window
        self.canvas = main_window.canvas
        self.loaded_files = []

        # Crop mode state
        self.crop_mode = False
        self.crop_rect_item = None
        self.crop_start_pos = None

    def toggle_crop_mode(self):
        """Toggle crop mode on/off."""
        # If crop mode is on, turn it off
        if self.crop_mode:
            self.crop_mode = False
            self._exit_crop_mode()
            self._update_crop_ui_state()
            return

        # Turning on: require a selected image
        if not self.canvas.scene.selectedItems():
            QMessageBox.information(self.main_window, "No Selection","Select an image first to crop it.")
            # The QAction auto-toggled on click; put the button back
            self._update_crop_ui_state()
            return

        self.crop_mode = True
        self._enter_crop_mode()
        self._update_crop_ui_state()

    def _enter_crop_mode(self):
        """Set up for crop mode."""
        # Clear any existing crop rectangle
        if self.crop_rect_item:
            self.canvas.scene.removeItem(self.crop_rect_item)
            self.crop_rect_item = None

        # Check if there's a selected image
        selected_items = self.canvas.scene.selectedItems()
        print(f"[DEBUG] Selected items count: {len(selected_items)}")

        # For now, just work with the first selected image
        self.selected_image = selected_items[0]

        # Print image info for debugging
        if hasattr(self.selected_image, 'filepath'):
            print(f"[DEBUG] Selected image: {self.selected_image.filepath}")

        img_rect = self.selected_image.boundingRect()
        scene_rect = self.selected_image.sceneBoundingRect()
        print(f"[DEBUG] Image local bounds: {img_rect}")
        print(f"[DEBUG] Image scene bounds: {scene_rect}")
        print(f"[DEBUG] Image position in scene: {self.selected_image.pos()}")

        # Change cursor to crosshair
        self.original_cursor = self.canvas.cursor()
        self.canvas.setCursor(Qt.CrossCursor)

        # Show status message
        self.main_window.status_bar.showMessage("Crop Mode: Click and drag to select area. Click Crop button again to exit.", 3000)

    def _exit_crop_mode(self):
        """Clean up after crop mode."""
        # Remove crop rectangle if it exists
        if self.crop_rect_item:
            self.canvas.scene.removeItem(self.crop_rect_item)
            self.crop_rect_item = None

        # Restore original cursor
        if hasattr(self, 'original_cursor'):
            self.canvas.setCursor(self.original_cursor)

        # Clear selection
        self.crop_start_pos = None
        self.selected_image = None

        # Show status message
        self.main_window.status_bar.showMessage("Crop mode exited", 2000)

    def _update_crop_ui_state(self):
        """Update UI to reflect crop mode state."""
        if hasattr(self.main_window, 'crop_action'):
            self.main_window.crop_action.setChecked(self.crop_mode)

    def handle_crop_mouse_press(self, event):
        """Handle mouse press in crop mode."""
        if not self.crop_mode:
            return

        # Get position in scene coordinates
        scene_pos = self.canvas.mapToScene(event.pos())
        print(f"[DEBUG] Mouse press - Screen: {event.pos()}, Scene: {scene_pos}")

        # Check if click is within the selected image (using scene coordinates)
        if self.selected_image:
            # Get image bounds in SCENE coordinates
            scene_img_rect = self.selected_image.sceneBoundingRect()
            print(f"[DEBUG] Image scene bounds: {scene_img_rect}")

            # Check if point is within the image bounds in SCENE coordinates
            contains = scene_img_rect.contains(scene_pos)
            print(f"[DEBUG] Contains point? {contains}")

            if not contains:
                print(f"[DEBUG] Click outside image bounds")
                return

        # Start new crop rectangle (use scene coordinates for rectangle)
        self.crop_start_pos = scene_pos
        print(f"[DEBUG] Crop start position set: {self.crop_start_pos}")

        # Create or update crop rectangle
        if self.crop_rect_item:
            self.canvas.scene.removeItem(self.crop_rect_item)

        # Create dashed rectangle

        pen = QPen(QColor(255, 0, 0))  # Red color
        pen.setWidth(2)
        pen.setStyle(Qt.DashLine)

        self.crop_rect_item = self.canvas.scene.addRect(scene_pos.x(), scene_pos.y(), 0, 0, pen)

        # Make sure rectangle is on top of everything
        self.crop_rect_item.setZValue(1000)

        print(f"[DEBUG] Crop rectangle created at: {scene_pos}")

    def handle_crop_mouse_move(self, event):
        """Handle mouse move in crop mode."""
        if not self.crop_mode or not self.crop_start_pos:
            return

        # Get current position in scene coordinates
        scene_pos = self.canvas.mapToScene(event.pos())

        print(f"[DEBUG] Mouse move - Scene: {scene_pos}")

        # Calculate rectangle dimensions
        x1, y1 = self.crop_start_pos.x(), self.crop_start_pos.y()
        x2, y2 = scene_pos.x(), scene_pos.y()

        # Ensure rectangle stays within image bounds (using scene coordinates)
        if self.selected_image:
            scene_img_rect = self.selected_image.sceneBoundingRect()
            print(f"[DEBUG] Image scene bounds: {scene_img_rect}")

            x2 = max(scene_img_rect.left(), min(x2, scene_img_rect.right()))
            y2 = max(scene_img_rect.top(), min(y2, scene_img_rect.bottom()))

            print(f"[DEBUG] Constrained position: ({x2}, {y2})")

        # Update rectangle
        rect = self.crop_rect_item.rect()
        rect.setTopLeft(QPointF(min(x1, x2), min(y1, y2)))
        rect.setBottomRight(QPointF(max(x1, x2), max(y1, y2)))
        self.crop_rect_item.setRect(rect)

        print(f"[DEBUG] Crop rectangle updated: {rect}")

    def handle_crop_mouse_release(self, event):
        """Handle mouse release in crop mode."""
        if not self.crop_mode or not self.crop_start_pos:
            return

        # Get release position
        scene_pos = self.canvas.mapToScene(event.pos())
        print(f"[DEBUG] Mouse release - Scene: {scene_pos}")

        if self.selected_image:
            item_pos = self.selected_image.mapFromScene(scene_pos)
            print(f"[DEBUG] Mouse release - Item: {item_pos}")

        # Crop rectangle is now complete
        if self.crop_rect_item:
            rect = self.crop_rect_item.rect()
            print(f"[DEBUG] Final crop rectangle: {rect}")
            print(f"[DEBUG] Crop rectangle dimensions: {rect.width():.0f}×{rect.height():.0f}")

            self.main_window.status_bar.showMessage(f"Crop area selected: {rect.width():.0f}×{rect.height():.0f}", 2000)

        self.crop_start_pos = None
        print(f"[DEBUG] Crop start position cleared")

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

    def _get_filepath_single(self):
        """Get single file path from dialog."""
        filepath, _ = QFileDialog.getOpenFileName(self.main_window, "Open Image", "", get_image_filter_string())
        return filepath if filepath else None

    def _get_filepaths_multiple(self):
        """Get multiple file paths from dialog."""
        filepaths, _ = QFileDialog.getOpenFileNames(self.main_window, "Open Multiple Images", "", get_image_filter_string())
        return filepaths if filepaths else []

    def _load_image_file(self, filepath):
        """Load an image file and update UI."""
        success = self.canvas.load_image(filepath)
        if success:
            self.loaded_files.append(Path(filepath))
            self.main_window.update_window_title()

    def delete_selection(self):
        """Delete selected image(s)."""
        selected_count = self.canvas.get_selected_count()
        if selected_count == 0:
            QMessageBox.information(self.main_window, "No Selection", "No images are selected. Select an image by clicking on it.")
            return

        # Confirm deletion
        if selected_count == 1:
            message = "Delete the selected image?"
        else:
            message = f"Delete {selected_count} selected images?"

        reply = QMessageBox.question(
            self.main_window, "Delete Selection", message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.canvas.delete_selected()
            self.main_window.update_selection_count()
            self.main_window.status_bar.showMessage(f"Deleted {selected_count} image(s)", 3000)

    def clear_canvas(self):
        """Clear all images from canvas."""
        if self.canvas.get_image_count() == 0:
            return

        reply = QMessageBox.question(
            self.main_window, "Clear Canvas",
            "Are you sure you want to clear all images from the canvas?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.canvas.clear_all()
            self.loaded_files.clear()
            self.main_window.update_window_title()
            self.main_window.pdate_selection_count()
            self.main_window.status_bar.showMessage("Canvas cleared", 3000)

    def on_image_added(self, filename, image_rect, _position):
        """Handle image added signal."""
        # Update image count
        count = self.canvas.get_image_count()
        self.main_window.image_count_label.setText(f"Images: {count}")

        # Show temporary message
        img_name = Path(filename).name
        self.main_window.status_bar.showMessage(f"Loaded: {img_name} ({image_rect.width():.0f}×{image_rect.height():.0f})", 3000)

    def on_image_removed(self, filepath):
        """Handle image removed signal."""
        # Remove from loaded files list
        path = Path(filepath)
        if path in self.loaded_files:
            self.loaded_files.remove(path)

        # Update image count
        count = self.canvas.get_image_count()
        self.main_window.image_count_label.setText(f"Images: {count}")
        self.main_window.update_window_title()

    def move_to_front(self):
        self.move_to("front")

    def move_to_back(self):
        self.move_to("back")

    def move_to(self, front_or_back):
        """Move selected image to front (highest z-value) or back (lowest z-value)."""
        # Find the highest current z-value
        all_items = self.canvas.scene.items()
        if not all_items:
            return

        selected_items = self.canvas.scene.selectedItems()
        if not selected_items:
            QMessageBox.information(self.main_window, "No Selection", "No images are selected. Select an image by clicking on it.")
            return

        if front_or_back == "front":
            max_z = max(item.zValue() for item in all_items)
            for item in selected_items:
                item.setZValue(max_z + 1)
        else:
            min_z = min(item.zValue() for item in all_items)
            for item in selected_items:
                item.setZValue(min_z - 1)

        if len(selected_items) == 1:
            self.main_window.status_bar.showMessage(f"Moved image to {front_or_back}", 2000)
        else:
            self.main_window.status_bar.showMessage(f"Moved selected images to {front_or_back}", 2000)