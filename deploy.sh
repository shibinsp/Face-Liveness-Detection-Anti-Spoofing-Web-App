#!/bin/bash

# Face Liveness Detection - Deployment Script
# Deploys application on ports: Backend 2524, Frontend 2525, Database 2523

set -e

echo "🚀 Starting Face Liveness Detection Deployment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose found${NC}"
echo ""

# Check if ports are available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
        echo "   You may need to stop the service using this port first"
        read -p "   Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Port $port is available${NC}"
    fi
}

echo "Checking ports..."
check_port 2524
check_port 2525
check_port 2523
echo ""

# Stop existing containers if running
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
echo ""

# Build and start services
echo "Building and starting services..."
if docker compose version &> /dev/null; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi
echo ""

# Wait for services to start
echo "Waiting for services to start..."
sleep 10
echo ""

# Check service health
check_health() {
    local name=$1
    local url=$2
    local expected=$3
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name is healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ $name health check failed${NC}"
        return 1
    fi
}

echo "Checking service health..."
echo ""

# Check backend
if check_health "Backend (Port 2524)" "http://localhost:2524/_stcore/health" "ok"; then
    BACKEND_OK=true
else
    BACKEND_OK=false
fi

# Check frontend
if check_health "Frontend (Port 2525)" "http://localhost:2525/health" "healthy"; then
    FRONTEND_OK=true
else
    FRONTEND_OK=false
fi

# Check database port
if check_health "Database Port (Port 2523)" "http://localhost:2523/health" "database-port-ready"; then
    DB_PORT_OK=true
else
    DB_PORT_OK=false
fi

echo ""
echo "=========================================="
echo "📊 Deployment Summary"
echo "=========================================="
echo ""

if [ "$BACKEND_OK" = true ] && [ "$FRONTEND_OK" = true ] && [ "$DB_PORT_OK" = true ]; then
    echo -e "${GREEN}✅ All services are running!${NC}"
    echo ""
    echo "Access the application at:"
    echo "  • Frontend: http://localhost:2525"
    echo "  • Backend:  http://localhost:2524"
    echo "  • Database Port: http://localhost:2523"
    echo ""
    echo "Or via your configured hosts:"
    echo "  • http://38.242.248.213:2525"
    echo "  • http://3netra.in:2525"
    echo "  • http://www.3netra.in:2525"
    echo ""
    echo "View logs: docker-compose logs -f"
    echo "Stop services: docker-compose down"
    echo ""
else
    echo -e "${YELLOW}⚠️  Some services may not be fully ready yet${NC}"
    echo ""
    echo "Please check logs: docker-compose logs -f"
    echo ""
fi

echo "=========================================="
echo ""

