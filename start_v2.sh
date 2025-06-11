#!/bin/bash
# Gemini Legion V2 - One Command to Rule Them All

echo "🚀 GEMINI LEGION V2 STARTUP SEQUENCE"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md" ]; then
    echo "❌ Run this from the geminopus-branch directory!"
    exit 1
fi

echo -e "${CYAN}Step 1: Starting V2 Backend...${NC}"
echo "-------------------------------"

# Kill any existing backend processes
pkill -f "gemini_legion_backend.main" 2>/dev/null
pkill -f "gemini_legion_backend.main_v2" 2>/dev/null

# Start V2 backend in background
echo "Starting backend on port 8000..."
python3 -m gemini_legion_backend.main_v2 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to initialize
echo -n "Waiting for backend to start"
for i in {1..10}; do
    sleep 1
    echo -n "."
    if curl -s http://localhost:8000/api/v2/status > /dev/null 2>&1; then
        echo -e "\n${GREEN}✅ Backend is running!${NC}"
        break
    fi
done

# Check if backend started successfully
if ! curl -s http://localhost:8000/api/v2/status > /dev/null 2>&1; then
    echo -e "\n${YELLOW}⚠️  Backend might not have started properly. Check backend.log${NC}"
    echo "Continuing anyway..."
fi

echo ""
echo -e "${CYAN}Step 2: Installing Frontend Dependencies...${NC}"
echo "-------------------------------------------"

cd gemini_legion_frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install
    npm install socket.io-client
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

echo ""
echo -e "${CYAN}Step 3: Starting Frontend...${NC}"
echo "-----------------------------"

# Kill any existing frontend processes
pkill -f "vite" 2>/dev/null

# Start frontend
echo "Starting frontend on port 5173..."
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

echo ""
echo -e "${GREEN}🎉 GEMINI LEGION V2 IS RUNNING!${NC}"
echo "================================"
echo ""
echo -e "${BLUE}Backend:${NC} http://localhost:8000"
echo -e "${BLUE}Frontend:${NC} http://localhost:5173"
echo -e "${BLUE}API Docs:${NC} http://localhost:8000/api/v2/docs"
echo ""
echo -e "${YELLOW}What to do now:${NC}"
echo "1. Open http://localhost:5173 in your browser"
echo "2. Click 'Spawn New Minion' to create your first minion"
echo "3. Type a message and watch your minions respond!"
echo ""
echo -e "${CYAN}To stop everything:${NC} Press Ctrl+C"
echo ""
echo -e "${GREEN}Backend PID:${NC} $BACKEND_PID"
echo -e "${GREEN}Frontend PID:${NC} $FRONTEND_PID"
echo ""
echo "Logs are in:"
echo "- Backend: ./backend.log"
echo "- Frontend: Check the terminal output"
echo ""
echo -e "${CYAN}Enjoy your fucking minions, Steven! 🤖${NC}"

# Keep script running and handle Ctrl+C
trap 'echo -e "\n${YELLOW}Shutting down...${NC}"; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT

# Keep the script running
while true; do
    sleep 1
done
