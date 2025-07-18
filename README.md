# CaseClipSaver

A lightweight, **single-file** Windows desktop application that automatically monitors the clipboard for case review data and saves it as structured files with intelligent file naming.

## Features

- 🔍 **Real-time Clipboard Monitoring** - Continuously monitors clipboard with 1-second polling
- 🎯 **Smart ID Extraction** - Extracts ICM IDs (9 digits) and Support Case IDs (13+ digits)
- 💾 **Intelligent File Naming** - Creates files with format `{ICM_ID}_{CASE_ID}.txt`
- 🎛️ **System Tray Control** - Simple ON/OFF toggle via system tray icon
- 📁 **Organized Output** - Auto-saves to `C:\casedata\` directory
- 🔔 **Optional Notifications** - Success/error notifications
- 📦 **Ultra-Portable** - Single Python file, minimal dependencies

## Quick Start

### Prerequisites
- Windows 10/11 (x64)
- Python 3.7+ (only if running from source)

### Option 1: Run Standalone Executable (Recommended)
```bash
# Build the executable
python build.py

# Run the executable
.\dist\CaseClipSaver.exe
```

### Option 2: Run from Source
```bash
# Install minimal dependencies
pip install -r requirements.txt

# Run the application
python caseclipsaver.py
```

### Option 3: Run Tests
```bash
# Test core functionality
python test_simple.py
```

## Project Structure (Ultra-Minimal)

```
caseClipper/
├── caseclipsaver.py      # Complete application (single file)
├── config.json           # Configuration file
├── build.py              # Build script for executable
├── test_simple.py        # Test suite
├── requirements.txt      # Minimal dependencies (3 packages)
└── README.md            # This file
```

## Dependencies

**Production (only 3 packages):**
- `pyperclip` - Clipboard access
- `pystray` - System tray functionality
- `Pillow` - Image handling for tray icon

**Development (optional):**
- `pyinstaller` - Build executable
- `pytest` - Testing
- `black` - Code formatting
- `flake8` - Linting

## Usage

1. **Start Application** - Run `python caseclipsaver.py` or the executable
2. **System Tray Icon** - Look for clipboard icon (Green = ON, Gray = OFF)
3. **Right-click Menu**:
   - Toggle monitoring ON/OFF
   - Test current clipboard content
   - Open output folder
   - View status
   - Exit application

## Supported Data Formats

### ICM ID Patterns (9 digits):
- `ICM 635658889`
- `ICM:635658889`
- `ICM635658889`

### Support Case ID Patterns (13+ digits):
- `Support Request Number: 2505160020000588`
- `Case: 2505160020000588`
- `Case #2505160020000588`
- `CRI: 2505160020000588`
- Standalone 13+ digit numbers

### Example Input:
```
ICM 635658889 - Critical production incident
Support Request Number: 2505160020000588
Customer: Contoso Corporation
Issue: Database connectivity problems
```

### Generated Output:
- **File**: `C:\casedata\635658889_2505160020000588.txt`
- **Content**: Complete clipboard text with timestamp metadata

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "output_directory": "C:\\casedata\\",
  "polling_interval": 1.0,
  "file_encoding": "utf-8",
  "enable_notifications": true,
  "auto_create_directory": true,
  "max_file_size_mb": 10
}
```

## File Naming Logic

| Found IDs | Filename Format |
|-----------|----------------|
| Both ICM + Case | `{ICM_ID}_{CASE_ID}.txt` |
| ICM only | `ICM_{ICM_ID}.txt` |
| Case only | `Case_{CASE_ID}.txt` |
| Duplicates | Append `_YYYYMMDD_HHMMSS` |

## Building Executable

```bash
# Simple build script
python build.py

# Output files:
# - dist/CaseClipSaver.exe  (standalone executable)
# - dist/config.json        (configuration file)
```

## Testing

```bash
# Run comprehensive tests
python test_simple.py

# Tests include:
# - Configuration loading
# - Data parser functionality
# - File manager operations
# - All supported ID patterns
```

## Architecture

The application is designed as a single-file solution with clear separation of concerns:

### Core Classes:
- **Config** - Configuration management
- **DataParser** - ID extraction with regex patterns
- **FileManager** - File operations and metadata
- **ClipboardMonitor** - Clipboard polling and processing
- **TrayUI** - System tray interface
- **CaseClipSaver** - Main application orchestrator

### Key Features:
- **Thread-safe operations** - Clipboard monitoring runs in separate thread
- **Duplicate detection** - Content hash caching prevents duplicate saves
- **Atomic file operations** - Temporary files ensure data integrity
- **Graceful error handling** - Comprehensive exception handling
- **Memory efficient** - Minimal resource usage

## System Requirements

- **OS**: Windows 10/11 (x64)
- **Memory**: < 50MB RAM
- **Disk**: < 5MB for source, < 50MB for executable
- **CPU**: < 1% when idle
- **Permissions**: Standard user (no admin required)

## Performance Characteristics

- **Startup**: < 2 seconds
- **Memory**: < 50MB during operation
- **CPU**: < 1% when idle
- **Polling**: 1-second intervals
- **File Operations**: < 100ms per save

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| App won't start | Check Python 3.7+ installation |
| No files being saved | Verify clipboard contains valid ICM/Case IDs |
| Tray icon missing | Check Windows "Show hidden icons" settings |
| Permission errors | Ensure write access to `C:\casedata\` |

### Debug Commands
```bash
# Test clipboard parsing
python test_simple.py

# Check dependencies
python -c "import pyperclip, pystray, PIL; print('Dependencies OK')"

# Test configuration
python -c "from caseclipsaver import Config; c=Config(); print('Config OK')"
```

## Advantages of Single-File Design

✅ **Ultra-Portable** - One Python file contains entire application
✅ **Minimal Dependencies** - Only 3 required packages
✅ **Easy Deployment** - Copy single file + config
✅ **Simple Maintenance** - All code in one location
✅ **Fast Startup** - No complex import chains
✅ **Easy Debugging** - Complete application visible in one file
✅ **Version Control Friendly** - Single file to track changes

## Development

### Making Changes
1. Edit `caseclipsaver.py` directly
2. Test with `python test_simple.py`
3. Build with `python build.py`

### Code Style
- PEP 8 compliant
- Type hints throughout
- Comprehensive error handling
- Clear class separation

### Adding Features
All functionality is contained in the single `caseclipsaver.py` file:
- Add new methods to existing classes
- Extend configuration options in `Config.DEFAULT_CONFIG`
- Add new regex patterns to `DataParser.patterns`
- Extend tray menu in `TrayUI._create_menu()`

## License

This project is created for internal case management workflow automation.

---

## Quick Commands

```bash
# Install and run
pip install -r requirements.txt
python caseclipsaver.py

# Test functionality
python test_simple.py

# Build executable
python build.py

# Run executable
.\dist\CaseClipSaver.exe
```

**Total project size: < 30KB source code, < 50MB executable**