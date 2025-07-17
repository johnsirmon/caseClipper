---
title: "CaseClipSaver - Clipboard Monitor for Case Review Data"
description: "A lightweight Windows application that automatically monitors clipboard for case review data and saves it as structured .txt files"
version: "1.0.0"
author: "John Sirmon"
created: "2025-07-17"
tech_stack: "Python 3.11+, pyperclip, pystray, tkinter"
---

# CaseClipSaver - Product Requirements Document

## Executive Summary
CaseClipSaver is a Windows desktop application that automatically monitors the clipboard for CRI (Case Review Incident) data, extracts ICM and Support Case IDs, and saves the content to named files for efficient case management workflow.

## Problem Statement
**Current Pain Points:**
- Manual copying of incident summaries during CRI and case reviews
- Error-prone manual file naming and saving process
- Workflow interruption when managing multiple cases
- Inconsistent file organization for case data
- **Manual navigation between Microsoft ICM portal and case review tools**
- **Repetitive copying from ICM incident details pages**
- **Context switching between browser and file management**

**Impact:** Reduced productivity and increased risk of data loss or misorganization during critical case reviews. Time wasted on manual data extraction from ICM portal reduces focus on actual case analysis.

## Solution Overview
An automated clipboard monitoring tool with browser integration that:
1. Runs silently in the system tray
2. Monitors clipboard for case review data patterns
3. **Integrates with Microsoft ICM portal for direct data extraction**
4. **Automatically detects ICM incident pages and extracts key information**
5. Automatically extracts ICM ID and Support Case ID
6. Saves content to standardized file names in a designated folder
7. Provides simple ON/OFF toggle control
8. **Offers browser extension-like functionality for ICM portal**

## Functional Requirements

### Core Features
| Feature | Priority | Description | Acceptance Criteria |
|---------|----------|-------------|-------------------|
| Clipboard Monitoring | P0 | Real-time clipboard content detection | App detects new clipboard content within 1 second |
| **ICM Portal Integration** | **P0** | **Direct extraction from ICM incident pages** | **Automatically detects ICM URLs and extracts incident data** |
| **Browser Session Hook** | **P1** | **Monitor active browser tabs for ICM portal** | **Detects when user navigates to ICM incident pages** |
| ID Extraction | P0 | Parse ICM ID and Support Case ID from text | Successfully extracts both IDs with 95% accuracy |
| File Auto-Save | P0 | Save content to named files | Creates file with format `ICMID_SupportCaseID.txt` |
| **Smart Context Detection** | **P1** | **Detect ICM incident context from URLs** | **Extract incident ID from URLs like `/incidents/details/624952217/`** |
| Toggle Control | P0 | ON/OFF monitoring control | User can start/stop monitoring via tray icon |
| Directory Management | P1 | Ensure output directory exists | Auto-create `C:\casedata\` if missing |
| **One-Click ICM Export** | **P1** | **Hotkey to extract current ICM page** | **Ctrl+Shift+S extracts current incident summary** |

### User Interface Requirements
- **System Tray Icon**: Always visible when running
- **Toggle States**: Clear visual indication of ON/OFF status
- **Right-click Menu**: Options for toggle, settings, exit
- **Notifications**: Optional success/error notifications
- **Browser Integration Panel**: Optional overlay for ICM portal pages
- **Hotkey Support**: Global hotkeys for quick actions (Ctrl+Shift+S for extract)
- **URL Pattern Detection**: Visual indicator when on supported ICM pages

### Data Processing Requirements

#### Input Format Detection
```python
# Expected clipboard patterns to detect:
CASE_PATTERNS = {
    "icm_id": r"ICM.*?(\d{9})",  # Matches: ICM 635658889 or ICM:635658889
    "support_case": r"Support Request Number:\s*(\d{15,})",  # Matches: Support Request Number: 2505160020000588
    "alternative_case": r"Case ID[:\s]*(\d{13,})"  # Alternative case ID format
}

# ICM Portal URL patterns to monitor:
ICM_URL_PATTERNS = {
    "incident_details": r"https://portal\.microsofticm\.com/imp/v5/incidents/details/(\d+)",
    "incident_search": r"https://portal\.microsofticm\.com/imp/v3/incidents/search",
    "incident_advanced": r"https://portal\.microsofticm\.com/imp/v3/incidents/search/advanced"
}

# Browser automation targets:
BROWSER_SELECTORS = {
    "incident_id": "[data-automation-id='incident-id']",
    "incident_title": "[data-automation-id='incident-title']", 
    "incident_summary": "[data-automation-id='incident-summary']",
    "severity": "[data-automation-id='severity']",
    "status": "[data-automation-id='status']"
}
```

#### Output File Specification
- **Location**: `C:\casedata\`
- **Naming Convention**: `{ICM_ID}_{SUPPORT_CASE_ID}.txt`
- **Content**: Complete clipboard text at time of detection
- **Encoding**: UTF-8
- **Duplicate Handling**: Append timestamp if file exists

## Technical Requirements

### Development Environment
- **Language**: Python 3.11+
- **Target OS**: Windows 11 (compatible with Windows 10)
- **Architecture**: x64
- **Deployment**: Standalone executable (PyInstaller)

### Core Dependencies
```python
# Required dependencies
REQUIRED_DEPS = [
    "pyperclip>=1.8.2",      # Clipboard access
    "pystray>=0.19.4",       # System tray functionality
    "Pillow>=9.5.0",         # Image handling for tray icon
    "selenium>=4.15.0",      # Browser automation for ICM integration
    "requests>=2.31.0",      # HTTP requests for API calls
    "beautifulsoup4>=4.12.0" # HTML parsing for web scraping
]

# Optional dependencies
OPTIONAL_DEPS = [
    "watchdog>=3.0.0",       # File system monitoring
    "plyer>=2.1.0",          # Cross-platform notifications
    "keyboard>=0.13.5",      # Global hotkey support
    "psutil>=5.9.0",         # Process monitoring for browser detection
    "win32gui>=0.0.0"        # Windows API for browser window management
]
```

### Performance Requirements
- **Memory Usage**: < 50MB RAM
- **CPU Usage**: < 1% when idle
- **Clipboard Check Frequency**: 1-second polling interval
- **Startup Time**: < 3 seconds to system tray
- **File Save Time**: < 500ms per file operation

### Security & Permissions
- **No Admin Rights Required**: Must run with standard user permissions
- **Clipboard Access**: Read-only clipboard monitoring
- **File System Access**: Write access to `C:\casedata\` only
- **Network Access**: None required (offline operation)

## Implementation Specifications

### Application Architecture
```
CaseClipSaver/
├── src/
│   ├── main.py              # Application entry point
│   ├── clipboard_monitor.py # Clipboard monitoring logic
│   ├── data_parser.py       # ID extraction and validation
│   ├── file_manager.py      # File operations and management
│   ├── tray_ui.py          # System tray interface
│   ├── config.py           # Configuration management
│   ├── browser_integration.py # ICM portal integration
│   ├── hotkey_manager.py   # Global hotkey handling
│   └── icm_scraper.py      # ICM page data extraction
├── resources/
│   ├── icon.ico            # Tray icon
│   ├── config.json         # Default settings
│   └── browser_extension/  # Optional browser extension files
├── tests/
│   └── test_*.py           # Unit tests
└── requirements.txt        # Dependencies
```

### Core Algorithms

#### Browser Integration Logic
```python
def monitor_browser_tabs():
    """
    Monitor browser tabs for ICM portal pages
    Returns: tuple (url: str, incident_id: str, page_type: str)
    """
    browsers = ['chrome.exe', 'msedge.exe', 'firefox.exe']
    for browser in browsers:
        if is_process_running(browser):
            tabs = get_browser_tabs(browser)
            for tab in tabs:
                if is_icm_url(tab.url):
                    incident_id = extract_incident_id_from_url(tab.url)
                    yield (tab.url, incident_id, get_page_type(tab.url))

def extract_icm_incident_data(incident_id: str) -> dict:
    """
    Extract incident data from ICM portal
    Args: incident_id (str): ICM incident ID
    Returns: dict with incident details
    """
    url = f"https://portal.microsofticm.com/imp/v5/incidents/details/{incident_id}/summary"
    
    # Use browser automation to extract data
    driver = get_browser_driver()
    driver.get(url)
    
    incident_data = {
        'incident_id': incident_id,
        'title': extract_text_by_selector(driver, "[data-automation-id='incident-title']"),
        'severity': extract_text_by_selector(driver, "[data-automation-id='severity']"),
        'status': extract_text_by_selector(driver, "[data-automation-id='status']"),
        'summary': extract_text_by_selector(driver, "[data-automation-id='incident-summary']"),
        'timestamp': datetime.now().isoformat(),
        'url': url
    }
    
    return incident_data
```

#### Clipboard Monitoring Logic
```python
def monitor_clipboard():
    """
    Continuously monitor clipboard for new content
    Returns: tuple (success: bool, content: str, timestamp: datetime)
    """
    last_content = ""
    while monitoring_enabled:
        current_content = get_clipboard_text()
        if current_content != last_content and current_content:
            yield process_clipboard_content(current_content)
            last_content = current_content
        time.sleep(1)  # 1-second polling interval
```

#### ID Extraction Logic
```python
def extract_case_ids(text: str) -> dict:
    """
    Extract ICM and Support Case IDs from clipboard text
    Args: text (str): Clipboard content
    Returns: dict with 'icm_id' and 'case_id' keys
    """
    patterns = {
        'icm_id': re.compile(r"ICM.*?(\d{9})", re.IGNORECASE),
        'case_id': re.compile(r"Support Request Number:\s*(\d{15,})", re.IGNORECASE)
    }
    
    results = {}
    for key, pattern in patterns.items():
        match = pattern.search(text)
        results[key] = match.group(1) if match else None
    
    return results
```

## User Stories

### Primary User Story
**As a** case review engineer  
**I want** clipboard content to be automatically saved with proper naming  
**So that** I can focus on case analysis without manual file management  

### Supporting User Stories
1. **Tray Control**: As a user, I want to easily toggle monitoring ON/OFF from the system tray
2. **File Organization**: As a user, I want files automatically organized in a predictable location
3. **Error Handling**: As a user, I want clear feedback when the app cannot save a file
4. **Performance**: As a user, I want the app to run without impacting system performance
5. **ICM Integration**: As a user, I want to automatically extract incident data when viewing ICM pages
6. **Hotkey Actions**: As a user, I want to press Ctrl+Shift+S to instantly save the current ICM incident
7. **Context Awareness**: As a user, I want the app to detect when I'm on an ICM incident page
8. **Structured Export**: As a user, I want ICM incident data saved in a consistent, readable format

## Testing Strategy

### Unit Tests
- [ ] Clipboard content detection accuracy
- [ ] ID extraction regex validation
- [ ] File naming and saving logic
- [ ] Error handling for edge cases

### Integration Tests
- [ ] End-to-end clipboard monitoring workflow
- [ ] System tray UI functionality
- [ ] File system permissions and error handling

### User Acceptance Tests
- [ ] Real case review data processing
- [ ] Performance under continuous operation
- [ ] User interface responsiveness

## Deployment & Distribution

### Build Process
```bash
# Build standalone executable
pip install pyinstaller
pyinstaller --onefile --windowed --icon=resources/icon.ico src/main.py
```

### Installation Requirements
- **Installer**: None required (portable executable)
- **Prerequisites**: Windows 11/10 x64
- **Permissions**: Standard user (no admin required)
- **Disk Space**: < 50MB

### Configuration
```json
{
  "output_directory": "C:\\casedata\\",
  "polling_interval": 1.0,
  "file_encoding": "utf-8",
  "enable_notifications": true,
  "auto_create_directory": true,
  "browser_integration": {
    "enabled": true,
    "monitor_browsers": ["chrome", "edge", "firefox"],
    "icm_domains": ["portal.microsofticm.com"],
    "auto_extract_on_navigate": false,
    "hotkey_extract": "ctrl+shift+s"
  },
  "icm_settings": {
    "include_summary": true,
    "include_timeline": false,
    "include_attachments": false,
    "structured_format": true,
    "export_format": "txt"
  }
}
```

## Workflow Optimization Recommendations

### Immediate Improvements (Current Version)
1. **Hotkey Integration**: Add global hotkey (Ctrl+Shift+S) to instantly capture current clipboard content
2. **Smart File Naming**: Include timestamp and severity level in filenames: `ICM624952217_CRITICAL_20250717_1430.txt`
3. **Browser Detection**: Monitor active browser tabs to detect ICM portal navigation
4. **Context Menu Actions**: Right-click tray icon → "Extract Current ICM Page"

### Phase 2 Enhancements (Next Sprint)
1. **Browser Automation**: Use Selenium to directly extract ICM incident data
   - Automatic login session detection
   - Extract structured incident details (title, severity, status, owner)
   - Save in both human-readable and machine-parseable formats

2. **ICM Portal Integration**:
   ```python
   # Example ICM data extraction
   def extract_icm_incident(incident_id: str) -> dict:
       return {
           'incident_id': incident_id,
           'title': get_incident_title(),
           'severity': get_severity_level(),
           'status': get_incident_status(),
           'owner': get_assigned_owner(),
           'created': get_creation_date(),
           'summary': get_incident_summary(),
           'timeline': get_incident_timeline(),
           'url': f'https://portal.microsofticm.com/imp/v5/incidents/details/{incident_id}'
       }
   ```

3. **Workflow Automation**:
   - Auto-detect when navigating to ICM incident pages
   - One-click export of incident details
   - Batch export from search results
   - Template-based incident reports

### Advanced Features (Phase 3)
1. **Browser Extension**: Native Chrome/Edge extension for seamless ICM integration
2. **API Integration**: Direct ICM API calls (if available) for faster data retrieval
3. **Team Collaboration**: Share extracted case data with team members
4. **Analytics Dashboard**: Track case review patterns and time savings

### Technical Implementation Priority
1. **Week 1**: Add browser process monitoring and URL detection
2. **Week 2**: Implement Selenium-based ICM page scraping
3. **Week 3**: Add hotkey support and context-aware extraction
4. **Week 4**: Create structured data export formats

---

## Success Metrics
- **Accuracy**: 95%+ successful ID extraction from valid case data
- **Performance**: <1% CPU usage during monitoring
- **Reliability**: 99%+ uptime during active monitoring sessions
- **User Satisfaction**: Reduces case review file management time by 80%
- **ICM Integration**: 90%+ success rate for browser-based incident extraction
- **Workflow Efficiency**: 60% reduction in manual copying from ICM portal

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| False positive ID detection | Medium | Low | Implement strict regex validation |
| Clipboard conflicts with other apps | High | Medium | Use non-blocking clipboard access |
| File permission errors | Medium | Medium | Graceful error handling and user notification |
| Performance degradation | Low | Low | Efficient polling and memory management |

## Future Enhancements (V2.0+)
- [ ] Configurable output directory
- [ ] Multiple case format support
- [ ] JSON export for data ingestion
- [ ] Duplicate detection and handling
- [ ] Batch processing of historical clipboard data
- [ ] Integration with case management systems
- [ ] Custom regex pattern configuration
- [ ] **Chrome/Edge extension for seamless ICM integration**
- [ ] **Automatic incident timeline extraction**
- [ ] **Multi-incident batch export from ICM search results**
- [ ] **Integration with Microsoft Teams for case updates**
- [ ] **OCR support for screenshot-based case data**
- [ ] **AI-powered incident summary generation**
- [ ] **Real-time collaboration features for case reviews**
- [ ] **Integration with Azure DevOps for incident tracking**

---

## Development Notes for AI Agents

### Implementation Priority
1. **Phase 1**: Core clipboard monitoring and file saving
2. **Phase 2**: System tray UI and toggle functionality
3. **Phase 3**: Error handling and edge cases
4. **Phase 4**: Performance optimization and testing

### Key Considerations for Code Generation
- Use type hints throughout the codebase
- Implement comprehensive error handling
- Follow Windows application best practices
- Ensure thread-safe clipboard access
- Design for testability and maintainability

### Sample Test Cases
```python
# Test data samples for validation
SAMPLE_CLIPBOARD_DATA = [
    "ICM 635658889 - Critical incident\nSupport Request Number: 2505160020000588",
    "Case ICM:123456789 Support Request Number: 1234567890123456",
    "Invalid data without proper IDs"
]
```
