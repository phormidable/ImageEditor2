"""
Toolbox containing business logic for MainWindow.
"""

from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox
from .helpers import get_image_filter_string

class MainWindowToolbox:
    """Contains business logic methods for MainWindow."""

    def __init__(self, main_window):
        self.main_window = main_window
        self.canvas = main_window.canvas
        self.loaded_files = []

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
        filepath, _ = QFileDialog.getOpenFileName(
            self.main_window, "Open Image", "", get_image_filter_string()
        )
        return filepath if filepath else None

    def _get_filepaths_multiple(self):
        """Get multiple file paths from dialog."""
        filepaths, _ = QFileDialog.getOpenFileNames(
            self.main_window, "Open Multiple Images", "", get_image_filter_string()
        )
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
            QMessageBox.information(
                self.main_window, "No Selection",
                "No images are selected. Select an image by clicking on it."
            )
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
        from pathlib import Path
        img_name = Path(filename).name
        self.main_window.status_bar.showMessage(
            f"Loaded: {img_name} ({image_rect.width():.0f}×{image_rect.height():.0f})",
            3000
        )

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
            QMessageBox.information(
                self.main_window, "No Selection",
                "No images are selected. Select an image by clicking on it."
            )
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