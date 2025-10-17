#!/bin/bash
#
# Quick Update Script for Pluto Voice Assistant
# Run this on Raspberry Pi to get latest fixes
#

echo "========================================"
echo "🔄 UPDATING PLUTO VOICE ASSISTANT"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    echo "❌ Error: Not in pluto-voice-assistant directory"
    echo "   Please cd to the project directory first"
    exit 1
fi

echo ""
echo "📡 Fetching latest changes from GitHub..."
git fetch origin

echo ""
echo "📊 Changes to be pulled:"
git log HEAD..origin/main --oneline

echo ""
echo "⬇️  Pulling latest code..."
git pull origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ UPDATE COMPLETE!"
    echo "========================================"
    echo ""
    echo "🎯 Recent fixes applied:"
    echo "   1. Vision worker thread now starts properly"
    echo "   2. Vision worker start() returns bool correctly"
    echo "   3. Debug script added for troubleshooting"
    echo ""
    echo "📋 What's new:"
    git log HEAD~3..HEAD --pretty=format:"   - %s" --no-merges
    echo ""
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Test: python debug_vision_worker.py"
    echo "   2. Run: python run.py"
    echo ""
    echo "========================================"
else
    echo ""
    echo "❌ Update failed! Please check for conflicts."
    echo "   You may need to commit or stash local changes first."
    exit 1
fi
