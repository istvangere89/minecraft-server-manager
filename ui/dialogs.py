"""
Dialog windows for password management and user interaction.
"""

import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt

from password_manager import hash_password, verify_password


class PasswordSetupDialog(QDialog):
    """Dialog for setting or updating a password on a configuration."""
    
    def __init__(self, parent=None, config_name: str = ""):
        """
        Initialize password setup dialog.
        
        Args:
            parent: Parent widget
            config_name: Name of the configuration being protected
        """
        super().__init__(parent)
        self.config_name = config_name
        self.password_hash = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI elements."""
        self.setWindowTitle("Set Password")
        self.setModal(True)
        self.setGeometry(100, 100, 400, 150)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"Set password for: {self.config_name}")
        layout.addWidget(title)
        
        # Password input
        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # Confirm password input
        layout.addWidget(QLabel("Confirm Password:"))
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _on_ok(self):
        """Handle OK button click."""
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        # Validation
        if not password:
            QMessageBox.warning(self, "Error", "Password cannot be empty")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            self.password_input.clear()
            self.confirm_input.clear()
            return
        
        # Hash and store
        self.password_hash = hash_password(password)
        self.accept()
    
    def get_password_hash(self) -> str:
        """Get the hashed password."""
        return self.password_hash


class PasswordPromptDialog(QDialog):
    """Dialog for entering a password to access a protected configuration."""
    
    def __init__(self, parent=None, config_name: str = ""):
        """
        Initialize password prompt dialog.
        
        Args:
            parent: Parent widget
            config_name: Name of the protected configuration
        """
        super().__init__(parent)
        self.config_name = config_name
        self.verified = False
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI elements."""
        self.setWindowTitle("Enter Password")
        self.setModal(True)
        self.setGeometry(100, 100, 400, 120)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"This configuration is protected.\nEnter password for: {self.config_name}")
        layout.addWidget(title)
        
        # Password input
        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._on_ok)
        layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Focus on password input
        self.password_input.setFocus()
    
    def _on_ok(self):
        """Handle OK button click."""
        password = self.password_input.text()
        if password:
            self.verified = True
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Please enter a password")
    
    def get_password(self) -> str:
        """Get the entered password."""
        return self.password_input.text()
    
    def is_verified(self) -> bool:
        """Check if password was entered."""
        return self.verified


class DirectorySelectDialog(QDialog):
    """Dialog for selecting the Minecraft server directory on first run."""
    
    def __init__(self, parent=None):
        """Initialize directory selection dialog."""
        super().__init__(parent)
        self.selected_path = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI elements."""
        self.setWindowTitle("Configure Server Directory")
        self.setModal(True)
        self.setGeometry(100, 100, 500, 150)
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "No server directory configured.\n"
            "Please select your Minecraft Bedrock server directory:"
        )
        layout.addWidget(instructions)
        
        # Path input
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        # Pre-fill with current working directory (where app is running from)
        current_dir = str(Path.cwd())
        self.path_input.setText(current_dir)
        self.path_input.selectAll()  # Select all text so user can easily replace if needed
        path_layout.addWidget(QLabel("Path:"))
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._on_browse)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _on_browse(self):
        """Handle browse button click."""
        from PyQt5.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Minecraft Server Directory",
            ""
        )
        if directory:
            self.path_input.setText(directory)
    
    def _on_ok(self):
        """Handle OK button click."""
        path = self.path_input.text().strip()
        
        if not path:
            QMessageBox.warning(self, "Error", "Please enter a valid directory path")
            return
        
        self.selected_path = path
        self.accept()
    
    def get_path(self) -> str:
        """Get the selected directory path."""
        return self.selected_path or ""
