@echo off
REM Build script for Minecraft Server Manager
REM Creates a standalone Windows executable using PyInstaller

echo Building Minecraft Server Manager...
pyinstaller build.spec --onefile --windowed

echo.
echo Build complete!
echo The executable can be found in: dist\minecraft_server_manager.exe
echo.
pause
