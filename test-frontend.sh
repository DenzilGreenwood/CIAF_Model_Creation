#!/bin/bash
# Frontend Test Runner for Linux/Mac
# Usage: ./test-frontend.sh [coverage] [watch]

cd "$(dirname "$0")/frontend"

if [ "$1" = "coverage" ]; then
    echo ""
    echo "======================================================================"
    echo "   Running Frontend Tests with Coverage Report"
    echo "======================================================================"
    echo ""
    npm run coverage
elif [ "$1" = "watch" ]; then
    echo ""
    echo "======================================================================"
    echo "   Running Frontend Tests in Watch Mode"
    echo "======================================================================"
    echo ""
    npm run test -- --watch
else
    echo ""
    echo "======================================================================"
    echo "   Running Frontend Tests"
    echo "======================================================================"
    echo ""
    npm run test
fi
