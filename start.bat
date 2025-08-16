@echo off
echo ========================================
echo   Code Weaver - 3D Code Visualization
echo ========================================
echo.

echo 🔧 Installing dependencies...
call npm run install:all

echo.
echo 🚀 Starting development servers...
echo   - Backend API: http://localhost:8000
echo   - Frontend: http://localhost:3000
echo.

call npm run dev