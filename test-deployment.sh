#!/bin/bash

# Deployment Verification Script
# This script tests if the Face Authentication System is properly deployed

echo "🔍 Face Authentication System - Deployment Verification"
echo "========================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local url=$1
    local description=$2

    echo -n "Testing: $description... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)

    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $response)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $response)"
        ((FAILED++))
    fi
}

# Test 1: Docker containers running
echo "1. Checking Docker containers..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Docker containers are running${NC}"
    docker-compose ps
    ((PASSED++))
else
    echo -e "${RED}✗ Docker containers are not running${NC}"
    ((FAILED++))
fi
echo ""

# Test 2: Backend health
echo "2. Testing Backend API..."
test_endpoint "http://localhost:8021/api/health" "Backend health endpoint"

# Test 3: User count
test_endpoint "http://localhost:8021/api/users/count" "User count endpoint"

# Test 4: API docs
test_endpoint "http://localhost:8021/docs" "API documentation"
echo ""

# Test 5: Frontend
echo "3. Testing Frontend..."
test_endpoint "http://localhost:2524/" "Frontend homepage"
echo ""

# Test 6: Check logs for errors
echo "4. Checking logs for errors..."
errors=$(docker-compose logs --tail=50 2>&1 | grep -i "error" | grep -v "0 error" | wc -l)
if [ "$errors" -eq 0 ]; then
    echo -e "${GREEN}✓ No errors found in logs${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ Found $errors error messages in logs${NC}"
    echo "Run 'docker-compose logs' to view details"
fi
echo ""

# Test 7: Database exists
echo "5. Checking database..."
if docker exec face-auth-backend test -f /app/backend/data/users.db; then
    echo -e "${GREEN}✓ Database file exists${NC}"

    # Count users
    user_count=$(docker exec face-auth-backend python -c "
import sqlite3
conn = sqlite3.connect('/app/backend/data/users.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
count = cursor.fetchone()[0]
conn.close()
print(count)
" 2>/dev/null)

    if [ -n "$user_count" ]; then
        echo -e "${GREEN}✓ Database contains $user_count registered users${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ Could not read user count${NC}"
    fi
else
    echo -e "${RED}✗ Database file not found${NC}"
    ((FAILED++))
fi
echo ""

# Summary
echo "========================================================"
echo "📊 Test Results Summary"
echo "========================================================"
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo ""

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Deployment is successful!${NC}"
    echo ""
    echo "Access your application:"
    echo "  - Frontend: http://localhost:2524"
    echo "  - Backend API: http://localhost:8021"
    echo "  - API Docs: http://localhost:8021/docs"
    exit 0
else
    echo -e "${RED}⚠ Some tests failed. Please check the logs.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check logs: docker-compose logs -f"
    echo "  2. Restart services: docker-compose restart"
    echo "  3. Rebuild: docker-compose build && docker-compose up -d"
    exit 1
fi
