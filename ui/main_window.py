"""
Main application window for the Minecraft Server Manager.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer

from config import ConfigManager
from server_manager import ServerManager
from password_manager import verify_password
from ui.dialogs import (
    PasswordSetupDialog, PasswordPromptDialog, DirectorySelectDialog
)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.setWindowTitle("Minecraft Server Manager")
        self.setGeometry(100, 100, 600, 500)
        
        # Initialize managers
        self.config = ConfigManager()
        self.server_manager = None
        
        # Initialize UI
        self._init_ui()
        
        # Check if server directory is configured
        if not self._validate_server_directory():
            self._show_directory_setup()
        else:
            self._load_configs()
    
    def _init_ui(self):
        """Initialize main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Select a Server Configuration:")
        main_layout.addWidget(title)
        
        # Config list
        self.config_list = QListWidget()
        self.config_list.itemDoubleClicked.connect(self._on_config_selected)
        main_layout.addWidget(self.config_list)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_configs)
        button_layout.addWidget(refresh_btn)
        
        start_btn = QPushButton("Select & Start")
        start_btn.clicked.connect(self._on_start_clicked)
        button_layout.addWidget(start_btn)
        
        manage_btn = QPushButton("Manage Passwords")
        manage_btn.clicked.connect(self._on_manage_passwords)
        button_layout.addWidget(manage_btn)
        
        config_btn = QPushButton("Change Server Directory")
        config_btn.clicked.connect(self._on_change_directory)
        button_layout.addWidget(config_btn)
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        central_widget.setLayout(main_layout)
    
    def _validate_server_directory(self) -> bool:
        """
        Validate the configured server directory.
        
        Returns:
            True if server directory is valid, False otherwise
        """
        server_dir = self.config.get_server_directory()
        
        if not server_dir:
            return False
        
        try:
            self.server_manager = ServerManager(server_dir)
            is_valid, error_msg = self.server_manager.validate_server_directory()
            
            if not is_valid:
                self._update_status(f"Error: {error_msg}")
                return False
            
            return True
        except Exception as e:
            self._update_status(f"Error: {str(e)}")
            return False
    
    def _show_directory_setup(self):
        """Show directory setup dialog."""
        dialog = DirectorySelectDialog(self)
        if dialog.exec_() == QFileDialog.Accepted:
            path = dialog.get_path()
            
            if path:
                # Validate the selected directory
                try:
                    temp_manager = ServerManager(path)
                    is_valid, error_msg = temp_manager.validate_server_directory()
                    
                    if is_valid:
                        self.config.set_server_directory(path)
                        self.server_manager = temp_manager
                        self._load_configs()
                        self._update_status("Server directory configured successfully")
                    else:
                        QMessageBox.critical(self, "Invalid Directory", error_msg)
                        self._show_directory_setup()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
                    self._show_directory_setup()
        else:
            # User cancelled - app cannot continue
            self._update_status("Server directory not configured. Please configure it to continue.")
    
    def _on_change_directory(self):
        """Handle change directory button."""
        dialog = DirectorySelectDialog(self)
        if dialog.exec_() == QFileDialog.Accepted:
            path = dialog.get_path()
            
            if path:
                try:
                    temp_manager = ServerManager(path)
                    is_valid, error_msg = temp_manager.validate_server_directory()
                    
                    if is_valid:
                        self.config.set_server_directory(path)
                        self.server_manager = temp_manager
                        self._load_configs()
                        self._update_status("Server directory updated")
                    else:
                        QMessageBox.critical(self, "Invalid Directory", error_msg)
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
    
    def _load_configs(self):
        """Load and display available configurations."""
        if not self.server_manager:
            self._update_status("Error: Server manager not initialized")
            return
        
        self.config_list.clear()
        
        try:
            configs = self.server_manager.discover_configs()
            
            if not configs:
                self._update_status("No configurations found")
                return
            
            # Add configs to list
            for config in configs:
                config_file = config["config_file"]
                world_name = config["world_name"]
                
                # Check if protected
                is_protected = self.config.is_config_protected(config_file)
                
                # Display with password indicator
                display_text = f"{world_name}"
                if is_protected:
                    display_text += " 🔒"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, config_file)
                self.config_list.addItem(item)
            
            self._update_status(f"Loaded {len(configs)} configuration(s)")
        except Exception as e:
            self._update_status(f"Error loading configs: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load configurations: {str(e)}")
    
    def _on_config_selected(self):
        """Handle config selection from list double-click."""
        self._on_start_clicked()
    
    def _on_start_clicked(self):
        """Handle start button click."""
        current_item = self.config_list.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "Select a Configuration", "Please select a configuration first")
            return
        
        config_file = current_item.data(Qt.UserRole)
        
        # Check if password protected
        if self.config.is_config_protected(config_file):
            password_hash = self.config.get_password_hash_for_config(config_file)
            
            # Show password prompt
            pwd_dialog = PasswordPromptDialog(self, config_file)
            if pwd_dialog.exec_() != PasswordPromptDialog.Accepted:
                self._update_status("Cancelled")
                return
            
            # Verify password
            entered_password = pwd_dialog.get_password()
            if not verify_password(entered_password, password_hash):
                QMessageBox.critical(self, "Wrong Password", "The password you entered is incorrect")
                self._update_status("Wrong password entered")
                return
        
        # Copy config and start server
        self._start_server_with_config(config_file)
    
    def _start_server_with_config(self, config_file: str):
        """
        Copy config to server.properties and start the server.
        
        Args:
            config_file: Name of the config file to use
        """
        try:
            # Copy config
            success, message = self.server_manager.copy_config_to_active(config_file)
            if not success:
                QMessageBox.critical(self, "Error", message)
                self._update_status(f"Error: {message}")
                return
            
            # Start server
            success, message = self.server_manager.start_server()
            if not success:
                QMessageBox.critical(self, "Error", message)
                self._update_status(f"Error: {message}")
                return
            
            self._update_status(f"Server started with {config_file}")
            QMessageBox.information(
                self,
                "Server Started",
                f"Server started with configuration: {config_file}\n\n{message}"
            )
        except Exception as e:
            error_msg = str(e)
            QMessageBox.critical(self, "Error", f"Failed to start server: {error_msg}")
            self._update_status(f"Error: {error_msg}")
    
    def _on_manage_passwords(self):
        """Handle manage passwords button click."""
        if self.config_list.count() == 0:
            QMessageBox.warning(self, "No Configurations", "No configurations found to protect")
            return
        
        # Get selected config or list all
        current_item = self.config_list.currentItem()
        if current_item:
            config_file = current_item.data(Qt.UserRole)
            world_name = current_item.text().replace(" 🔒", "")
            self._set_password_for_config(config_file, world_name)
        else:
            QMessageBox.warning(self, "Select a Configuration", "Please select a configuration to protect")
    
    def _set_password_for_config(self, config_file: str, world_name: str):
        """
        Show password setup dialog for a configuration.
        
        Args:
            config_file: Name of the config file
            world_name: Display name of the world
        """
        dialog = PasswordSetupDialog(self, world_name)
        if dialog.exec_() == PasswordSetupDialog.Accepted:
            password_hash = dialog.get_password_hash()
            if password_hash:
                self.config.set_password_for_config(config_file, password_hash)
                self._update_status(f"Password set for {world_name}")
                self._load_configs()  # Refresh to show lock icon
                QMessageBox.information(self, "Success", f"Password set for {world_name}")
    
    def _update_status(self, message: str):
        """
        Update the status bar message.
        
        Args:
            message: Status message to display
        """
        self.status_label.setText(message)
