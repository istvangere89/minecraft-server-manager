"""
Main application window for the Minecraft Server Manager.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ..config import ConfigManager
from ..password_manager import verify_password
from ..server_manager import ServerManager
from .dialogs import DirectorySelectDialog, PasswordPromptDialog, PasswordSetupDialog
from .terminal_widget import TerminalWidget


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.setWindowTitle("Minecraft Server Manager")
        self.setGeometry(100, 100, 900, 600)

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
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("Select a Server Configuration:")
        main_layout.addWidget(title)

        # Create splitter for config list and terminal
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Config list (fixed width ~40 characters)
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.config_list = QListWidget()
        self.config_list.itemDoubleClicked.connect(self._on_config_selected)
        left_layout.addWidget(self.config_list)

        # Buttons for config management
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 5, 0, 0)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_configs)
        button_layout.addWidget(refresh_btn)

        manage_btn = QPushButton("Manage Passwords")
        manage_btn.clicked.connect(self._on_manage_passwords)
        button_layout.addWidget(manage_btn)

        config_btn = QPushButton("Change Server Directory")
        config_btn.clicked.connect(self._on_change_directory)
        button_layout.addWidget(config_btn)

        left_layout.addLayout(button_layout)
        left_widget.setLayout(left_layout)

        # Set fixed width for left panel (approximately 40 characters wide)
        # Using QFontMetrics to calculate proper width
        font = QFont("Courier New", 9)
        metrics = QFontMetrics(font)
        char_width = metrics.averageCharWidth()
        list_width = char_width * 40 + 20  # 40 chars + padding
        left_widget.setMaximumWidth(int(list_width))

        # Right panel: Terminal (fills remaining space)
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Terminal widget (should expand to fill height and width)
        self.terminal = TerminalWidget()
        right_layout.addWidget(self.terminal, 1)  # Stretch factor 1

        # Server control buttons
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 5, 0, 0)

        start_btn = QPushButton("Start Server")
        start_btn.clicked.connect(self._on_start_server)
        control_layout.addWidget(start_btn)

        stop_btn = QPushButton("Stop Server")
        stop_btn.clicked.connect(self._on_stop_server)
        control_layout.addWidget(stop_btn)

        control_layout.addStretch()
        right_layout.addLayout(control_layout)
        right_widget.setLayout(right_layout)

        # Add both to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        # Left panel fixed, right panel stretches
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter, 1)  # Stretch factor 1 for main splitter

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

        # Debug: Print what we got
        print(f"[DEBUG] Server directory from config: '{server_dir}'")

        if not server_dir or server_dir.strip() == "":
            print("[DEBUG] Server directory is empty, showing setup dialog")
            return False

        try:
            self.server_manager = ServerManager(server_dir)
            is_valid, error_msg = self.server_manager.validate_server_directory()

            if not is_valid:
                self._update_status(f"Error: {error_msg}")
                print(f"[DEBUG] Validation failed: {error_msg}")
                return False

            print("[DEBUG] Server directory validation successful")
            return True
        except Exception as e:
            self._update_status(f"Error: {str(e)}")
            print(f"[DEBUG] Exception during validation: {str(e)}")
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

    def _on_start_server(self):
        """Handle start server button click - uses embedded terminal."""
        current_item = self.config_list.currentItem()

        if not current_item:
            QMessageBox.warning(self, "Select a Configuration", "Please select a configuration first")
            return

        config_file = current_item.data(Qt.UserRole)
        world_name = current_item.text().replace(" 🔒", "")

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

        # Copy config
        success, message = self.server_manager.copy_config_to_active(config_file)
        if not success:
            QMessageBox.critical(self, "Error", message)
            self._update_status(f"Error: {message}")
            return

        # Clear terminal
        self.terminal.clear()
        self.terminal.append_output(f"Starting server with configuration: {world_name}")
        self.terminal.append_output("=" * 60)

        # Start server with embedded terminal
        success, message = self.server_manager.start_server_embedded(output_callback=self.terminal.append_output)

        if not success:
            QMessageBox.critical(self, "Error", message)
            self._update_status(f"Error: {message}")
            return

        self._update_status(f"Server running with {world_name}")

    def _on_stop_server(self):
        """Handle stop server button click."""
        if not self.server_manager.is_running:
            QMessageBox.warning(self, "Server Not Running", "The server is not currently running")
            return

        success, message = self.server_manager.stop_server()

        if success:
            self.terminal.append_output("=" * 60)
            self.terminal.append_output(message)
            self._update_status(message)
        else:
            QMessageBox.critical(self, "Error", message)
            self._update_status(f"Error: {message}")

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

    def closeEvent(self, event):
        """
        Handle window close event.
        Warns user if server is running and offers options.

        Args:
            event: Close event
        """
        if self.server_manager and self.server_manager.is_running:
            # Server is running - ask what to do
            reply = QMessageBox(self)
            reply.setWindowTitle("Server Running")
            reply.setText("The server is still running. What would you like to do?")
            reply.setIcon(QMessageBox.Warning)

            reply.addButton("Keep Running", QMessageBox.AcceptRole)
            stop_btn = reply.addButton("Stop Server", QMessageBox.DestructiveRole)
            cancel_btn = reply.addButton("Cancel", QMessageBox.RejectRole)

            reply.exec_()

            if reply.clickedButton() == cancel_btn:
                # Cancel close
                event.ignore()
                return
            elif reply.clickedButton() == stop_btn:
                # Stop server and close
                self.server_manager.stop_server()
                self.terminal.append_output("=" * 60)
                self.terminal.append_output("Server stopped. Closing application.")
                event.accept()
            else:
                # Keep running and close (default)
                self.terminal.append_output("=" * 60)
                self.terminal.append_output("Application closed. Server continues running.")
                event.accept()
        else:
            # Server not running - just close
            event.accept()
