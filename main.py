"""
Minecraft Server Manager - Main Application Entry Point
A simple desktop UI for managing Bedrock server configurations on Windows.
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication

from logger_config import setup_logging, get_logger
from ui.main_window import MainWindow


# Initialize logging before anything else
setup_logging()
logger = get_logger()

# Set up global exception handler to catch crashes
def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to log crashes before exiting."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical(
        "Uncaught exception:",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception


def main():
    """Application entry point."""
    logger.info("Starting Minecraft Server Manager")
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Minecraft Server Manager")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
