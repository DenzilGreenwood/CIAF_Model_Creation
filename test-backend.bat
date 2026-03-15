@echo off
REM Backend Test Runner for Windows
REM Usage: test-backend.bat [coverage]

cd /d "%~dp0ciaf\vault"

echo.
echo ======================================================================
echo   Running Backend Tests (Vault API)
echo ======================================================================
echo.

if "%1%"=="coverage" (
    echo Generating coverage report...
    call pytest api.test.py -v -p no:langsmith --cov=ciaf/vault --cov-report=html --cov-report=term
    echo.
    echo Coverage report generated in htmlcov/index.html
) else (
    call pytest api.test.py -v -p no:langsmith
)

echo.
echo ======================================================================
echo Done!
echo ======================================================================
echo.
pause
