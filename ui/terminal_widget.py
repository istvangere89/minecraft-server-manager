"""
Terminal display widget for showing server output.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QTextCursor


class TerminalWidget(QWidget):
    """Widget for displaying server terminal output."""
    
    def __init__(self, parent=None):
        """Initialize terminal widget."""
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI elements."""
        layout = QVBoxLayout()
        
        # Terminal text display
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        
        # Set terminal-like appearance
        font = QFont("Courier New", 9)
        self.text_display.setFont(font)
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 1px solid #333333;
                padding: 5px;
            }
        """)
        
        layout.addWidget(self.text_display)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(layout)
    
    def append_output(self, text: str):
        """
        Append text to terminal output.
        
        Args:
            text: Text to append
        """
        # Add text and scroll to bottom
        cursor = self.text_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text + "\n")
        self.text_display.setTextCursor(cursor)
        self.text_display.ensureCursorVisible()
    
    def clear(self):
        """Clear terminal output."""
        self.text_display.clear()
    
    def get_text(self) -> str:
        """
        Get all terminal text.
        
        Returns:
            All text in terminal
        """
        return self.text_display.toPlainText()
