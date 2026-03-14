#!/bin/bash

# CIAF MVP - Quick Start Script

echo "🚀 CIAF MVP - Quick Start Guide"
echo "================================"
echo ""

# Check if service is running
echo "✅ Checking CIAF Verification Service..."
if curl -s http://localhost:8001/health > /dev/null; then
    echo "   Service is running at http://localhost:8001"
else
    echo "   ⚠️  Service not running. Make sure Docker containers are started:"
    echo "      docker-compose -f docker-compose.full.yml up -d"
    exit 1
fi

echo ""
echo "✅ Installing dependencies..."
pip install -r mvp_requirements.txt -q

echo ""
echo "✅ Dependencies installed"
echo ""
echo "🎬 Running CIAF MVP Demonstrations..."
echo "===================================="
echo ""

python demo_workflows.py

echo ""
echo "✅ MVP Demo Complete!"
echo ""
echo "📊 Access the Web Dashboard: http://localhost:3000"
echo "📚 API Documentation: http://localhost:8001/docs"
echo ""
echo "💡 Next Steps:"
echo "   1. View generated outputs in the dashboard"
echo "   2. Check compliance reports"
echo "   3. Explore audit trails"
echo "   4. Verify cryptographic proofs"
echo ""
