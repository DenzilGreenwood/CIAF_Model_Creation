@echo off
REM Frontend Test Runner for Windows
REM Usage: test-frontend.bat [coverage] [watch]

cd /d "%~dp0frontend"

if "%1%"=="coverage" (
    echo.
    echo ======================================================================
    echo   Running Frontend Tests with Coverage Report
    echo ======================================================================
    echo.
    call npm run coverage
    goto end
)

if "%1%"=="watch" (
    echo.
    echo ======================================================================
    echo   Running Frontend Tests in Watch Mode
    echo ======================================================================
    echo.
    call npm run test -- --watch
    goto end
)

echo.
echo ======================================================================
echo   Running Frontend Tests
echo ======================================================================
echo.
call npm run test

:end
pause
