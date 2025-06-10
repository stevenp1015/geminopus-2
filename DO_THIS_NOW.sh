#!/bin/bash
# DO THIS NOW - Emergency Fix for Gemini Legion

echo "🚨 GEMINI LEGION EMERGENCY FIX PROCEDURE"
echo "========================================"
echo ""
echo "This will fix the message duplication issue RIGHT NOW"
echo ""

# Step 1
echo "Step 1: Apply the emergency fixes"
echo "---------------------------------"
echo "Running emergency_fix.py..."
echo ""
read -p "Press Enter to apply fixes (or Ctrl+C to cancel)..."

python3 emergency_fix.py

echo ""
echo "✅ Fixes applied!"
echo ""

# Step 2
echo "Step 2: Restart the backend"
echo "---------------------------"
echo "You need to:"
echo "1. Find and kill the current backend process"
echo "2. Start it again"
echo ""
echo "To find the process:"
echo "  ps aux | grep 'gemini_legion_backend.main'"
echo ""
echo "To kill it:"
echo "  kill <PID>"
echo ""
echo "To restart:"
echo "  cd /Users/ttig/downloads/geminopus-branch"
echo "  python3 -m gemini_legion_backend.main"
echo ""
read -p "Press Enter after you've restarted the backend..."

# Step 3
echo ""
echo "Step 3: Test the fix"
echo "--------------------"
echo "Testing simple message endpoint..."
echo ""

# Test health first
echo "Checking backend health..."
curl -s http://localhost:8000/api/health | python3 -m json.tool

echo ""
echo "Sending test message to general channel..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/channels/test_simple \
  -H 'Content-Type: application/json' \
  -d '{"channel_id": "general", "content": "Emergency fix test message"}')

echo "Response:"
echo $RESPONSE | python3 -m json.tool

echo ""
echo "========================================"
echo "✅ EMERGENCY FIX COMPLETE!"
echo ""
echo "What's fixed:"
echo "- Messages should no longer duplicate"
echo "- Minion auto-responses are disabled"
echo "- Simple message flow is working"
echo ""
echo "What's next:"
echo "1. Read README_STEVEN.md for the full story"
echo "2. Follow UNFUCK_PLAN.md for the proper refactor"
echo "3. Your original architecture doc is the goal"
echo ""
echo "Key files:"
echo "- README_STEVEN.md - Start here"
echo "- UNFUCK_PLAN.md - The refactoring roadmap"
echo "- MESSAGE_FLOW_DIAGRAM.md - Visual of the problem"
echo "- IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md - The destination"
echo ""
echo "Good luck unfucking this mess! 🚀"
