# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CaseClipSaver is a Windows desktop application that monitors the clipboard for case review data and automatically saves it as structured files. The application runs as a system tray service and detects specific patterns in clipboard content to extract ICM and Support Case IDs.

## Development Environment

### Dual Development Setup
- **WSL Development**: VS Code Insiders with WSL remote extension (this environment)
- **Windows Development**: VS Code Insiders native Windows (C:\source\caseClipper)
- **Sync Method**: GitHub commits/pushes between environments
- **Execution**: Windows ONLY - application will never run on WSL

### Key Points
- Application uses Windows-specific libraries (pystray, pyperclip, plyer)
- All testing and execution must be done on Windows
- WSL is used only for development assistance with Claude Code
- PowerShell scripts (.ps1) are for Windows building only

## Development Commands

### Development Environment Setup (Windows Only)
```powershell
# Windows development setup
cd C:\source\caseClipper

# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies  
pip install -r requirements-dev.txt

# Run from source (Windows only)
python src/main.py
```

### Testing (Windows Only)
```powershell
# Run all tests (Windows)
.\run_tests.ps1

# Run specific test files (Windows)
python -m unittest tests.test_data_parser -v
python -m unittest tests.test_file_manager -v

# Run tests with pytest (if available, Windows)
pytest tests/ -v
```

### Code Quality (Any Environment)
```bash
# Format code (works in WSL or Windows)
black src/

# Check code style (works in WSL or Windows)
flake8 src/

# Type checking (works in WSL or Windows)
mypy src/

# Sort imports (works in WSL or Windows)
isort src/
```

### Building and Deployment (Windows Only)
```powershell
# Build standalone executable (Windows only)
.\build.ps1

# Test the executable (Windows only)
.\dist\CaseClipSaver.exe

# Run build and test together (Windows only)
.\make.ps1 build
.\make.ps1 test-exe
```

## Architecture

### Core Components

The application follows a modular architecture with clear separation of concerns:

1. **main.py** - Application entry point and orchestration
   - Handles PyInstaller vs development mode imports
   - Manages application lifecycle and graceful shutdown
   - Coordinates all components

2. **clipboard_monitor.py** - Clipboard monitoring engine
   - Polls clipboard content in a separate thread
   - Detects changes and triggers processing
   - Manages monitoring state (start/stop)

3. **data_parser.py** - Data extraction and validation
   - Regex patterns for ICM and Support Case ID extraction
   - Supports multiple ID formats and patterns
   - Generates standardized filenames from extracted IDs

4. **file_manager.py** - File operations and storage
   - Handles file saving with metadata
   - Manages output directory creation
   - Implements deduplication with timestamps

5. **tray_ui.py** - System tray interface
   - Creates and manages system tray icon
   - Provides context menu for user interaction
   - Handles notifications and user feedback

6. **config.py** - Configuration management
   - Loads settings from resources/config.json
   - Handles both development and PyInstaller modes
   - Provides property-based access to settings

### Data Flow

1. **Clipboard Monitor** continuously polls clipboard content
2. **Data Parser** validates and extracts ICM/Case IDs from clipboard text
3. **File Manager** saves content and metadata to `C:\casedata\`
4. **Tray UI** provides user feedback and control interface

### Import Handling

The codebase handles both development and PyInstaller executable modes:

```python
# Standard pattern used throughout
try:
    # Try relative imports first (development)
    from .module import Class
except ImportError:
    # Fall back to absolute imports (PyInstaller)
    from module import Class
```

## Key Patterns and Conventions

### ID Extraction Patterns
- **ICM ID**: 9-digit number following "ICM" (e.g., "ICM 635658889")
- **Support Case ID**: 13+ digit number following "Support Request Number:" 
- **Alternative formats**: "Case:", "Case #", "CRI:", or standalone 13+ digit numbers

### File Naming Convention
- **Both IDs**: `{ICM_ID}_{CASE_ID}.txt`
- **ICM only**: `ICM_{ICM_ID}.txt`
- **Case only**: `Case_{CASE_ID}.txt`
- **Duplicates**: Append timestamp `_YYYYMMDD_HHMMSS`

### Configuration Options
Located in `resources/config.json`:
- `output_directory`: File save location (default: `C:\casedata\`)
- `polling_interval`: Clipboard check frequency (default: 1.0 seconds)
- `enable_notifications`: Show system notifications (default: true)
- `auto_create_directory`: Create output directory if missing (default: true)

## Development Environment

### Development Workflow
- **WSL Development**: Use WSL for development with Claude Code and MCP servers
- **Windows Development**: Use native Windows for development and testing
- **Sync Method**: GitHub commits/pushes (not file copying)
- **Testing**: Windows ONLY for system tray functionality
- **Build**: Windows ONLY using PowerShell scripts

### Windows-Specific Features
- **System Tray**: Only works on Windows (pystray library)
- **Clipboard Access**: Windows clipboard API through pyperclip
- **Notifications**: Windows toast notifications via plyer
- **File Operations**: Windows path handling and Explorer integration

## Testing Strategy

### Unit Tests
- `test_data_parser.py`: ID extraction and validation logic
- `test_file_manager.py`: File operations and storage

### Manual Testing
- Copy test case data to clipboard
- Verify file creation in output directory
- Test tray UI functionality and notifications
- Validate executable build process

## Build Process

### PyInstaller Configuration
Uses `CaseClipSaver.spec` for:
- Hidden imports for all modules
- Resource file inclusion (config.json, icon assets)
- Windows-specific binary packaging
- Console hiding for GUI application

### Resource Handling
- Configuration files bundled in `resources/` directory
- Icon assets created programmatically in tray_ui.py
- Proper path resolution for both development and executable modes

## Troubleshooting

### Common Issues
- **Import errors**: Check relative vs absolute import handling
- **Resource not found**: Verify resource path resolution in config.py
- **Tray icon missing**: Ensure Windows notification area settings
- **Clipboard access fails**: Check pyperclip Windows dependencies

### Development vs Production
- Use `getattr(sys, 'frozen', False)` to detect PyInstaller mode
- Different path handling for resources and modules
- Development allows multiple instances, production includes instance checking