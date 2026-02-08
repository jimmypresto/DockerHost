#!/bin/bash
set -e

echo "=== Separate Repository Setup for /Volumes/DockerHost/claude ==="
echo ""
echo "This will:"
echo "  1. Remove claude/ from parent repo at /Volumes/DockerHost"
echo "  2. Initialize new git repo at /Volumes/DockerHost/claude"
echo "  3. Set up two-branch strategy (local + main)"
echo "  4. Configure remote for GitHub"
echo ""

read -p "Current git root: $(cd /Volumes/DockerHost && git rev-parse --show-toplevel). Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Step 1: Remove claude/ from parent repo
echo ""
echo "Step 1: Removing claude/ from parent repo..."
cd /Volumes/DockerHost

# Check if there are any uncommitted changes in claude/
if git status --short | grep -q '^.. claude/'; then
    echo "⚠ Found uncommitted changes in claude/ in parent repo:"
    git status --short | grep '^.. claude/'
    read -p "Commit these to parent repo first? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add claude/
        git commit -m "Save claude/ state before converting to separate repo"
    fi
fi

# Remove from git tracking but keep files
git rm -r --cached claude/
echo "claude/" >> .gitignore
echo "✓ Removed claude/ from parent repo tracking"

# Commit the removal
git commit -m "Remove claude/ from tracking (now a separate repo)"
echo "✓ Committed .gitignore update"

# Step 2: Initialize new git repo in claude/
echo ""
echo "Step 2: Initializing new git repo at /Volumes/DockerHost/claude..."
cd /Volumes/DockerHost/claude

# Remove any git files if they exist
rm -rf .git

# Initialize new repo
git init
echo "✓ Initialized git repo"

# Initial commit with everything
git add .
git commit -m "Initial commit of claude workspace"
echo "✓ Created initial commit"

# Step 3: Set up two-branch strategy
echo ""
echo "Step 3: Setting up two-branch strategy..."

# Rename main to local (this branch has everything)
git branch -m main local
echo "✓ Created 'local' branch (includes generated files)"

# Create main branch for GitHub (without generated files)
git checkout -b main local

# Remove generated files from this branch
if git ls-files | grep -q '^runs/'; then
    echo "Removing generated files from 'main' branch:"
    git ls-files | grep '^runs/'
    git rm -r runs/test-storage-20260124-101928
    git commit -m "Remove generated files from remote branch"
    echo "✓ Removed generated files from 'main' branch"
else
    echo "⚠ No runs/ files found to remove"
fi

# Step 4: Add remote
echo ""
echo "Step 4: Configuring GitHub remote..."
git remote add origin https://github.com/jimmypresto/claude.git
echo "✓ Added remote: https://github.com/jimmypresto/claude.git"

# Summary
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Repository structure:"
echo "  /Volumes/DockerHost        - Parent repo (local backup)"
echo "  /Volumes/DockerHost/claude - Separate repo (for GitHub)"
echo ""
echo "Branches in claude repo:"
git branch -a
echo ""
echo "Remote:"
git remote -v
echo ""
echo "Next steps:"
echo "  1. Verify: git log --oneline -5"
echo "  2. Push to GitHub: git push -u origin main"
echo "  3. Daily work: git checkout local (includes all files)"
echo "  4. To sync to GitHub: git checkout main && cherry-pick from local"
