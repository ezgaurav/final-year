#!/bin/bash

echo "==================================="
echo "Medicine Detection AI - Startup"
echo "==================================="

# Check if backend dependencies are installed
if [ ! -d "backend/__pycache__" ]; then
    echo "Installing backend dependencies..."
    cd backend
    pip install -r requirements.txt
    cd ..
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "Starting services..."
echo ""

# Start backend in background
echo "Starting backend on http://localhost:8000"
cd backend
python -m uvicorn app:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "Starting frontend on http://localhost:3000"
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "==================================="
echo "Services Started!"
echo "==================================="
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "==================================="

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
