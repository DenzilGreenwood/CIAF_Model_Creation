#!/usr/bin/env bash
# CIAF Docker Setup - Complete Getting Started

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║           🐳 CIAF DOCKER SETUP - COMPLETE STACK                             ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "   Install Docker from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo "   Install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"
echo ""

# Show services
echo -e "${YELLOW}📋 Services to be started:${NC}"
echo "   1. PostgreSQL Database (port 5432)"
echo "   2. Redis Cache (port 6379)"
echo "   3. Vault API (port 8002)"
echo "   4. Verification Service (port 8001)"
echo "   5. Frontend (port 3002)"
echo ""

# Start Docker Compose
echo -e "${YELLOW}🚀 Starting Docker Compose...${NC}"
echo ""

# Check if we should rebuild
if [[ "$1" == "--rebuild" ]]; then
    echo "   Building images..."
    docker-compose build --no-cache
    echo ""
fi

# Start services
docker-compose up -d

# Wait for services
echo ""
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 5

# Check service health
echo ""
echo -e "${YELLOW}🏥 Checking service health...${NC}"
echo ""

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U ciaf_verification -d ciaf_proofs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL${NC} - Ready on port 5432"
else
    echo -e "${RED}❌ PostgreSQL${NC} - Not ready"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis${NC} - Ready on port 6379"
else
    echo -e "${RED}❌ Redis${NC} - Not ready"
fi

# Check Vault API
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Vault API${NC} - Ready on port 8002"
else
    echo -e "${RED}❌ Vault API${NC} - Not ready (trying again...)"
fi

# Check Verification Service
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Verification Service${NC} - Ready on port 8001"
else
    echo -e "${RED}❌ Verification Service${NC} - Not ready (trying again...)"
fi

# Check Frontend
if curl -s http://localhost:3002 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend${NC} - Ready on port 3002"
else
    echo -e "${YELLOW}⏳ Frontend${NC} - Still starting... (will be ready in 30-60 seconds)"
fi

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                                                                              ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}                   🎉 CIAF Stack is Starting!                                 ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}                                                                              ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "📍 Service Endpoints:"
echo ""
echo "   🖥️  Frontend:          http://localhost:3002"
echo "   🔌 Vault API:         http://localhost:8002"
echo "   📊 Verification:      http://localhost:8001"
echo "   📦 Database:          localhost:5432"
echo "   💾 Cache:             localhost:6379"
echo ""

echo "📊 Database Credentials:"
echo "   User: ciaf_verification"
echo "   Password: ciaf_secure_password_dev"
echo "   Database: ciaf_proofs"
echo ""

echo "🔑 API Key:"
echo "   Bearer: test-api-key-org-1"
echo ""

echo "🧪 Run Tests:"
echo "   python examples/api_client_example.py"
echo ""

echo "📚 Useful Commands:"
echo "   docker-compose logs -f             # View logs"
echo "   docker-compose ps                  # Show running containers"
echo "   docker-compose down                # Stop all services"
echo "   docker-compose exec postgres psql -U ciaf_verification -d ciaf_proofs"
echo ""

echo "✨ Next Steps:"
echo "   1. Open http://localhost:3002 in your browser"
echo "   2. Run: python examples/api_client_example.py"
echo "   3. Check logs: docker-compose logs -f vault"
echo ""
