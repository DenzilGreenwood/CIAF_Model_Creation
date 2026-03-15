#!/bin/bash
# Backend Test Runner for Linux/Mac
# Usage: ./test-backend.sh [coverage]

cd "$(dirname "$0")/ciaf/vault"

echo ""
echo "======================================================================"
echo "   Running Backend Tests (Vault API)"
echo "======================================================================"
echo ""

if [ "$1" = "coverage" ]; then
    echo "Generating coverage report..."
    pytest api.test.py -v -p no:langsmith --cov=ciaf/vault --cov-report=html --cov-report=term
    echo ""
    echo "Coverage report generated in htmlcov/index.html"
else
    pytest api.test.py -v -p no:langsmith
fi

echo ""
echo "======================================================================"
echo "Done!"
echo "======================================================================"
echo ""
