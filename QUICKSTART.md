# CaseClipSaver Development Quick Start

## 🚀 Hybrid Development Workflow

### Windows Setup (Testing & Deployment)
```bash
# Open VS Code Insiders (NOT connected to WSL)
code-insiders C:\source\caseClipper

# Pull latest changes from WSL work
git pull

# Test Windows-specific features
python src/main.py                    # Test in development
.\dist\CaseClipSaver.exe             # Test executable

# Build for deployment
.\build.ps1                           # Creates standalone .exe
```

### WSL/Ubuntu Setup (Development & AI)
```bash
# Open VS Code Insiders with WSL connection
code-insiders .

# Clone repo to WSL (first time only)
git clone /mnt/c/source/caseClipper ~/caseclipper
cd ~/caseclipper

# Daily development
git pull                              # Get Windows changes
# ... do development work with Claude ...
git add . && git commit -m "..."     # Save progress
git push                              # Not needed (local only)
```

## ✅ DO in WSL (Ubuntu):
- ✅ Code development with Claude AI
- ✅ Unit testing: `python -m pytest tests/`
- ✅ Git commits: `git add . && git commit -m "..."`
- ✅ Core logic development (data parsing, file management)
- ✅ Requirements management: `pip install -r requirements.txt`
- ✅ Code formatting: `black src/` and `flake8 src/`

## ❌ DON'T in WSL (Ubuntu):
- ❌ Run system tray app: `python src/main.py`
- ❌ Build executables: `.\build.ps1`
- ❌ Test clipboard monitoring (no Windows clipboard)
- ❌ Install Windows-specific packages: `pystray`, `pyperclip`
- ❌ Browser automation (Windows process monitoring)

## ✅ DO in Windows:
- ✅ Full application testing: `python src/main.py`
- ✅ Executable building: `.\build.ps1`
- ✅ System tray testing
- ✅ Clipboard monitoring testing
- ✅ Final deployment preparation
- ✅ Git pulls: `git pull` (get WSL changes)

## ❌ DON'T in Windows:
- ❌ Heavy development work (use WSL for Claude AI)
- ❌ Frequent Git commits (do in WSL)

## 🔄 Daily Workflow:

### Morning (Start Development):
1. **Windows**: `git status` (check for uncommitted changes)
2. **WSL**: `git pull` (get any Windows changes)
3. **WSL**: Develop with Claude AI assistance

### Evening (Test & Deploy):
1. **WSL**: `git add . && git commit -m "Today's changes"`
2. **Windows**: `git pull` (get WSL changes)
3. **Windows**: Test full application
4. **Windows**: Build executable if needed

## 📁 Project Structure:
```
Windows: C:\source\caseClipper\       # Main repo, testing, building
WSL:     ~/caseclipper/               # Development clone, AI work
```

## 🆘 Troubleshooting:

**Performance Issues?**
- Work in `~/caseclipper/` in WSL (not `/mnt/c/...`)
- Use Git to sync, not file copying

**Git Conflicts?**
- Always commit in WSL before switching to Windows
- Always pull in Windows before testing

**Missing Dependencies in WSL?**
```bash
cd ~/caseclipper
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Can't Test Full App in WSL?**
- This is expected! Use Windows for system tray testing
- WSL is for development only

## 🎯 Summary:
- **WSL = Development + Claude AI**
- **Windows = Testing + Deployment**  
- **Git = Sync mechanism**
- **Performance = Work in WSL home, not /mnt/c/**
