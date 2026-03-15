@echo off
REM CIAF Docker Setup - Windows Version
REM Complete Getting Started with Docker

color 0B
cls

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║           🐳 CIAF DOCKER SETUP - COMPLETE STACK (Windows)                   ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ Docker is not installed!
    echo.
    echo Install Docker from: https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ Docker Compose is not installed!
    echo.
    echo Install Docker Compose from: https://docs.docker.com/compose/install/
    echo.
    pause
    exit /b 1
)

color 0A
echo ✅ Docker is installed
color 0B
echo.

echo 📋 Services to be started:
echo.
echo    1. PostgreSQL Database (port 5432)
echo    2. Redis Cache (port 6379)
echo    3. Vault API (port 8002)
echo    4. Verification Service (port 8001)
echo    5. Frontend (port 3002)
echo.

echo 🚀 Starting Docker Compose...
echo.

REM Check for rebuild flag
if "%1%"=="--rebuild" (
    echo    Building images...
    call docker-compose build --no-cache
    echo.
)

REM Start services
call docker-compose up -d

REM Wait for services
echo.
echo ⏳ Waiting for services to start...
timeout /t 5 /nobreak
echo.

echo 🏥 Checking service health...
echo.

REM Check PostgreSQL
docker-compose exec -T postgres pg_isready -U ciaf_verification -d ciaf_proofs >nul 2>&1
if %errorlevel% equ 0 (
    color 0A
    echo ✅ PostgreSQL - Ready on port 5432
) else (
    color 0C
    echo ❌ PostgreSQL - Not ready
)

REM Check Redis
docker-compose exec -T redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    color 0A
    echo ✅ Redis - Ready on port 6379
) else (
    color 0C
    echo ❌ Redis - Not ready
)

REM Check Vault API
curl -s http://localhost:8002/health >nul 2>&1
if %errorlevel% equ 0 (
    color 0A
    echo ✅ Vault API - Ready on port 8002
) else (
    color 0E
    echo ⏳ Vault API - Not ready yet (trying again...)
)

REM Check Verification Service
curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% equ 0 (
    color 0A
    echo ✅ Verification Service - Ready on port 8001
) else (
    color 0E
    echo ⏳ Verification Service - Not ready yet (trying again...)
)

REM Check Frontend
curl -s http://localhost:3002 >nul 2>&1
if %errorlevel% equ 0 (
    color 0A
    echo ✅ Frontend - Ready on port 3002
) else (
    color 0E
    echo ⏳ Frontend - Still starting... ^(will be ready in 30-60 seconds^)
)

echo.
color 0B
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║                   🎉 CIAF Stack is Starting!                                ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 📍 SERVICE ENDPOINTS:
echo.
echo    🖥️  Frontend:          http://localhost:3002
echo    🔌 Vault API:         http://localhost:8002
echo    📊 Verification:      http://localhost:8001
echo    📦 Database:          localhost:5432
echo    💾 Cache:             localhost:6379
echo.

echo 📊 DATABASE CREDENTIALS:
echo    User: ciaf_verification
echo    Password: ciaf_secure_password_dev
echo    Database: ciaf_proofs
echo.

echo 🔑 API KEY:
echo    Bearer: test-api-key-org-1
echo.

echo 🧪 RUN TESTS:
echo    python examples/api_client_example.py
echo.

echo 📚 USEFUL COMMANDS:
echo    docker-compose logs -f                  # View logs
echo    docker-compose ps                      # Show running containers
echo    docker-compose down                    # Stop all services
echo.

echo ✨ NEXT STEPS:
echo    1. Open http://localhost:3002 in your browser
echo    2. Run: python examples/api_client_example.py
echo    3. Check logs: docker-compose logs -f vault
echo.

color 0B
pause
