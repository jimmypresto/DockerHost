#!/bin/bash
set -e

echo "=== Two-Branch Strategy Setup ==="
echo ""
echo "Current state:"
git branch -a
echo ""
git remote -v
echo ""

read -p "Step 1: Rename main -> local? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git branch -m main local
    echo "✓ Renamed main to local"
    git branch
fi

read -p "Step 2: Create clean main branch? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git checkout -b main local
    echo "✓ Created main from local"

    # Check if runs directory exists in git
    if git ls-files | grep -q '^runs/'; then
        echo "Found generated files to remove:"
        git ls-files | grep '^runs/'

        git rm -r runs/test-storage-20260124-101928
        git commit -m "Remove generated files from remote branch"
        echo "✓ Removed generated files"
    else
        echo "⚠ No runs files found to remove"
    fi
fi

read -p "Step 3: Update remote to claude.git? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git remote remove origin || echo "No origin to remove"
    git remote add origin https://github.com/jimmypresto/claude.git
    echo "✓ Updated remote to claude.git"
    git remote -v
fi

read -p "Step 4: Push to GitHub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Pushing main branch to GitHub..."
    git push -u origin main
    echo "✓ Pushed to GitHub"
fi

echo ""
echo "=== Setup Complete ==="
echo "Branches:"
git branch -a
echo ""
echo "Remotes:"
git remote -v
echo ""
echo "Usage:"
echo "  - Work on 'local' branch for everything (including generated files)"
echo "  - Cherry-pick/merge to 'main' for GitHub pushes"
