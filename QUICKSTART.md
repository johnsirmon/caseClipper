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
# 1. Open VS Code Insiders with "Connect to WSL"
# 2. In WSL VS Code terminal, navigate to projects:
cd ~
mkdir -p projects  # Create projects folder if needed
cd projects

# 3. BEST PRACTICE: Copy from Windows (one-time setup)
cp -r /mnt/c/source/caseClipper ./caseClipper
cd caseClipper

# 4. Verify Git repo is intact
git status
git log --oneline

# 5. Open the WSL copy in VS Code
# File > Open Folder > /home/yourusername/projects/caseClipper

# Daily development workflow:
git pull                              # Get any Windows changes  
# ... do development work with Claude ...
git add . && git commit -m "..."     # Save progress locally
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

### Initial Setup (One Time):
**In WSL VS Code (after "Connect to WSL"):**
```bash
# Navigate to your projects area
cd ~
mkdir -p projects
cd projects

# Copy Windows repo to WSL (FAST - one time only)
cp -r /mnt/c/source/caseClipper ./caseClipper
cd caseClipper

# Verify everything copied correctly
git status
ls -la src/

# Open this WSL folder in VS Code
# File > Open Folder > /home/yourusername/projects/caseClipper
```

**No Windows prep needed** - your Git repo is ready to copy!

### Morning (Start Development):
1. **Windows**: `git status` (check for uncommitted changes)
2. **WSL**: `cd ~/caseclipper && git pull` (get any Windows changes)
3. **WSL**: Develop with Claude AI assistance

### Evening (Test & Deploy):
1. **WSL**: `git add . && git commit -m "Today's changes"`
2. **WSL**: `git push` (if using remote) OR manual sync ↓
3. **Windows**: `git pull` (get WSL changes)
4. **Windows**: Test full application
5. **Windows**: Build executable if needed

### Manual Sync (No Remote Git):
```bash
# WSL → Windows (after development)
# In WSL: git bundle create changes.bundle HEAD~n..HEAD
# Copy bundle to Windows, then: git pull ./changes.bundle

# OR use shared mounted directory for Git patches
git format-patch HEAD~1 --stdout > /mnt/c/temp/latest.patch
# In Windows: git apply C:\temp\latest.patch
```

## 📁 Project Structure:
```
Windows: C:\source\caseClipper\              # Main repo, testing, building
WSL:     ~/projects/caseClipper/             # Development copy, AI work
```

## 🆘 Troubleshooting:

**Performance Issues?**
- ✅ **BEST**: Work in `~/caseclipper/` in WSL (native Linux filesystem)
- ❌ **AVOID**: Working in `/mnt/c/...` (cross-filesystem performance hit)
- ✅ Use one-time `cp -r` to copy initially, then Git for sync
- ❌ Don't use `git clone /mnt/c/...` (slow cross-boundary operation)

**Git Sync Strategies:**
- **Best**: Use GitHub/GitLab remote for seamless sync
- **Good**: Use Git bundles or patches for local-only sync  
- **Avoid**: Frequent file copying across `/mnt/c/`

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
