"""
Smart Clock Dashboard Application Entry Point.

This is a minimal entry point following PyQt5 best practices.
The main application logic has been refactored into the MVC architecture
located in the smrtclk package.

Usage:
    python run.py [--config CONFIG_FILE] [--debug]
"""

import sys

from PyQt5.QtWidgets import QApplication

from config.settings import Config
from smrtclk.views.main_window import ClockMainWindow


def main():
    """
    Main application entry point.

    Initializes the QApplication, creates the main window with configuration,
    displays it, and enters the event loop.

    Follows PyQt5 best practices:
    - QApplication created first before any GUI objects
    - Proper use of sys.exit(app.exec()) for clean termination
    - Configuration loaded before window creation
    """
    # Create the QApplication instance
    app = QApplication(sys.argv)

    # Load configuration (from environment or defaults)
    config = Config.from_env()

    # Create and show the main window
    window = ClockMainWindow(config)
    window.show()

    # Enter the event loop and exit properly
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
