#!/usr/bin/env python3
"""
Image Compositor - Main Entry Point
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow


def main():
    """Application entry point."""

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Image Compositor")
    app.setOrganizationName("MyOrg")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Handle command line arguments
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if Path(arg).exists():
                window.canvas.load_image(arg)

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()