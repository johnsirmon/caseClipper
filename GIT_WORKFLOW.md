# Git Workflow Guide for CaseClipSaver

## Local Git Setup (No Remote Required)
Your project is now under local version control! Here's how to use Git effectively:

## Essential Git Commands

### Daily Workflow
```bash
# Check status of your files
git status

# See what changed since last commit
git diff

# Add specific files to staging
git add src/main.py
git add prd.md

# Add all changed files
git add .

# Commit your changes
git commit -m "Description of what you changed"

# View commit history
git log --oneline
git log --graph --oneline --all
```

### Branching for Features
```bash
# Create and switch to a new branch for a feature
git checkout -b feature/browser-integration

# List all branches
git branch

# Switch between branches
git checkout master
git checkout feature/browser-integration

# Merge a feature branch back to master
git checkout master
git merge feature/browser-integration

# Delete a feature branch after merging
git branch -d feature/browser-integration
```

### Useful Git Commands
```bash
# See detailed history
git log --stat

# See changes in a specific commit
git show bae0aba

# Create a tag for a release
git tag -a v1.0.0 -m "Release version 1.0.0"

# List all tags
git tag

# Revert changes to a file
git checkout -- src/main.py

# Undo last commit (keeping changes)
git reset --soft HEAD~1

# Undo last commit (discarding changes) - BE CAREFUL!
git reset --hard HEAD~1
```

## Recommended Workflow

### For Bug Fixes:
1. `git checkout -b bugfix/clipboard-monitoring-issue`
2. Make your changes
3. `git add .`
4. `git commit -m "Fix: Resolve clipboard monitoring memory leak"`
5. `git checkout master`
6. `git merge bugfix/clipboard-monitoring-issue`

### For New Features:
1. `git checkout -b feature/icm-browser-integration`
2. Work on the feature in small commits
3. `git add src/browser_integration.py`
4. `git commit -m "Add browser tab monitoring for ICM portal"`
5. Continue with more commits as you develop
6. When complete: merge back to master

### For Documentation Updates:
1. `git add prd.md`
2. `git commit -m "Update PRD with browser integration requirements"`

## Benefits of Local Git:

✅ **Full Version History**: Track every change with detailed messages
✅ **Branching**: Experiment with features without breaking main code
✅ **Backup**: Your entire project history is preserved locally
✅ **Rollback**: Easily undo changes or revert to previous versions
✅ **No Internet Required**: Works completely offline
✅ **Professional Development**: Industry-standard version control

## Optional: Adding Remote Repository Later

If you decide to add cloud backup/sharing later:

```bash
# GitHub (free private repos)
git remote add origin https://github.com/yourusername/caseclipsaver.git
git push -u origin master

# Azure DevOps
git remote add origin https://dev.azure.com/yourorg/yourproject/_git/caseclipsaver
git push -u origin master

# GitLab
git remote add origin https://gitlab.com/yourusername/caseclipsaver.git
git push -u origin master
```

But for now, local Git gives you all the version control benefits without any setup complexity!
