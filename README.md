# CaseClipSaver

A lightweight Windows application that automatically monitors the clipboard for case review data and saves it as structured .txt files.

## Features

- 🔍 **Automatic Clipboard Monitoring** - Real-time detection of case review data
- 🎯 **Smart ID Extraction** - Automatically extracts ICM and Support Case IDs
- 💾 **Auto-Save Functionality** - Saves content with standardized naming: `{ICM_ID}_{CASE_ID}.txt`
- 🎛️ **System Tray Control** - Simple ON/OFF toggle via system tray icon
- 📁 **Organized Output** - All files saved to `C:\casedata\` directory
- 🔔 **Notifications** - Optional success/error notifications

## Quick Start

### Option 1: Run from Source (Recommended for Development)

1. **Install Python 3.11+** from [python.org](https://python.org)

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```powershell
   python src/main.py
   ```

### Option 2: Build Standalone Executable

1. **Run the build script:**
   ```powershell
   .\build.ps1
   ```

2. **Run the executable:**
   ```powershell
   .\dist\CaseClipSaver.exe
   ```

## Usage

1. **Start the Application** - The app runs in your system tray
2. **Look for the Clipboard Icon** - Green = ON, Gray = OFF
3. **Right-click the Icon** to:
   - Turn monitoring ON/OFF
   - Test current clipboard content
   - Open output folder
   - View status
   - Exit application

4. **Copy Case Review Data** - The app automatically detects and saves data containing:
   - ICM ID (9 digits): `ICM 635658889`
   - Support Case ID (13+ digits): `Support Request Number: 2505160020000588`

## Expected Input Format

The application looks for clipboard content containing both:

```
ICM 635658889 - Critical incident description
Support Request Number: 2505160020000588
Additional case details...
```

Alternative formats also supported:
```
Case ICM:123456789
Case ID: 1234567890123456
```

## Output

Files are saved to `C:\casedata\` with the format:
```
635658889_2505160020000588.txt
635658889_2505160020000588_metadata.json
```

## Configuration

Edit `resources/config.json` to customize:

```json
{
  "output_directory": "C:\\casedata\\",
  "polling_interval": 1.0,
  "file_encoding": "utf-8",
  "enable_notifications": true,
  "auto_create_directory": true
}
```

## Testing

Run unit tests:
```powershell
.\run_tests.ps1
```

Or run individual tests:
```powershell
python -m unittest tests.test_data_parser -v
python -m unittest tests.test_file_manager -v
```

## Requirements

- **OS**: Windows 10/11 (x64)
- **Python**: 3.11+ (for source)
- **Memory**: < 50MB RAM
- **Disk**: < 50MB
- **Permissions**: Standard user (no admin required)

## Dependencies

- `pyperclip` - Clipboard access
- `pystray` - System tray functionality  
- `Pillow` - Image handling for tray icon
- `plyer` - Cross-platform notifications (optional)

## Architecture

```
src/
├── main.py              # Application entry point
├── clipboard_monitor.py # Clipboard monitoring logic
├── data_parser.py       # ID extraction and validation
├── file_manager.py      # File operations
├── tray_ui.py          # System tray interface
└── config.py           # Configuration management
```

## Troubleshooting

### Application Won't Start
- Ensure Python 3.11+ is installed
- Run `pip install -r requirements.txt`
- Check Windows Defender hasn't blocked the executable

### No Files Being Saved
- Check clipboard contains both ICM and Support Case IDs
- Verify `C:\casedata\` directory permissions
- Right-click tray icon → "Test Clipboard" to debug

### System Tray Icon Missing
- Check Windows "Show hidden icons" settings
- Try restarting the application
- Ensure no other instances are running

### Build Issues
- Update pip: `python -m pip install --upgrade pip`
- Install latest PyInstaller: `pip install --upgrade pyinstaller`
- Run build script as Administrator if permission errors occur

## Support

For issues or feature requests, check the console output for error messages and ensure all requirements are met.

## License

This project is created for internal case management workflow automation.
