#!/bin/bash
# Quick local testing script (not for production)

echo "🎰 Degens777Den - Local Test Environment"
echo "=========================================="

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "❌ MongoDB is not running!"
    echo "   Start it with: sudo systemctl start mongod"
    exit 1
fi

echo "✅ MongoDB is running"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd /app/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

# Install frontend dependencies  
echo "📦 Installing frontend dependencies..."
cd /app/frontend
if [ ! -d "node_modules" ]; then
    yarn install --silent
fi

# Start backend
echo "🚀 Starting backend on port 8001..."
cd /app/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# Wait for backend
echo "⏳ Waiting for backend to start..."
sleep 5

# Seed database
echo "🌱 Seeding database..."
curl -s -X POST http://localhost:8001/api/seed > /dev/null

# Start frontend
echo "🚀 Starting frontend on port 3000..."
cd /app/frontend
PORT=3000 yarn start &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "✅ DEGENS777DEN IS RUNNING!"
echo "=========================================="
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8001/api"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "👤 Admin Login:"
echo "   Email: admin@degensden.com"
echo "   Password: admin123"
echo ""
echo "📊 Test APIs:"
echo "   curl http://localhost:8001/api/"
echo "   curl http://localhost:8001/api/kodakgp/rates"
echo ""
echo "🛑 To stop: pkill -f uvicorn && pkill -f react-scripts"
echo "=========================================="

# Keep script running
wait
