@echo off

echo 🐳 Starting Cody with Docker...

REM Docker Compose 실행
docker-compose up -d

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak > nul

REM 서비스 상태 확인
echo 📊 Checking service status...
docker-compose ps

echo.
echo 🌐 Services are available at:
echo   - Neo4j Browser: http://localhost:7474
echo   - Cody API: http://localhost:8000
echo   - Frontend: Open frontend.html in your browser
echo.
echo 🔑 Neo4j credentials:
echo   - Username: neo4j
echo   - Password: codycody
echo.
echo ✅ Cody is ready!
echo 📝 To stop services: docker-compose down

pause
