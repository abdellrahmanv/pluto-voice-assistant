#!/bin/bash
# Setup Git identity for pushing logs

echo "🔧 Setting up Git identity..."

# Set your name and email
git config --global user.name "abdellrahmanv"
git config --global user.email "your-email@example.com"

echo "✅ Git configured!"
echo ""
echo "Now you can push logs:"
echo "  git add pluto_run.log"
echo "  git commit -m 'Add log file'"
echo "  git push"
