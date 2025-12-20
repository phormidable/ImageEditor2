"""
Image Compositor application package.
"""

from .main_window import MainWindow
from .canvas_view import CanvasView
from .main_window_toolbox import MainWindowToolbox
from .helpers import *

__version__ = "0.1.2"
__all__ = ['MainWindow', 'CanvasView', 'MainWindowToolbox']