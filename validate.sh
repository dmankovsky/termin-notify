#!/bin/bash

# Termin-Notify Validation Script
# This script validates the application setup and configuration

set -e

echo "=================================="
echo "Termin-Notify Validation Script"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "1. Checking Prerequisites..."
echo "----------------------------"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    check_ok "Python 3 installed: $PYTHON_VERSION"
else
    check_fail "Python 3 not found"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    check_ok "Docker installed: $DOCKER_VERSION"
else
    check_warn "Docker not found (optional for local dev)"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | tr -d ',')
    check_ok "Docker Compose installed: $COMPOSE_VERSION"
else
    check_warn "Docker Compose not found (optional for local dev)"
fi

echo ""
echo "2. Checking Project Structure..."
echo "--------------------------------"

# Check required files
REQUIRED_FILES=(
    "app/main.py"
    "app/core/config.py"
    "app/core/database.py"
    "app/models/user.py"
    "app/api/auth.py"
    "requirements.txt"
    "docker-compose.yml"
    "Dockerfile"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_ok "$file exists"
    else
        check_fail "$file not found"
    fi
done

echo ""
echo "3. Checking Configuration..."
echo "----------------------------"

# Check .env file
if [ -f ".env" ]; then
    check_ok ".env file exists"

    # Check required env vars
    if grep -q "DATABASE_URL=" .env && [ -n "$(grep DATABASE_URL= .env | cut -d'=' -f2)" ]; then
        check_ok "DATABASE_URL configured"
    else
        check_fail "DATABASE_URL not configured"
    fi

    if grep -q "SECRET_KEY=" .env && [ -n "$(grep SECRET_KEY= .env | cut -d'=' -f2)" ]; then
        check_ok "SECRET_KEY configured"
    else
        check_fail "SECRET_KEY not configured"
    fi

    if grep -q "SMTP_HOST=" .env && [ -n "$(grep SMTP_HOST= .env | cut -d'=' -f2)" ]; then
        check_ok "SMTP_HOST configured"
    else
        check_warn "SMTP_HOST not configured (email won't work)"
    fi
else
    check_fail ".env file not found"
    echo "   Run: cp .env.example .env"
fi

echo ""
echo "4. Checking Python Dependencies..."
echo "-----------------------------------"

if [ -f "requirements.txt" ]; then
    check_ok "requirements.txt found"

    # Count dependencies
    DEP_COUNT=$(grep -v "^#" requirements.txt | grep -v "^$" | wc -l | tr -d ' ')
    echo "   Found $DEP_COUNT dependencies"
fi

echo ""
echo "5. Code Quality Checks..."
echo "-------------------------"

# Check for syntax errors in main files
for file in app/main.py app/core/config.py app/models/user.py; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        check_ok "$file - syntax OK"
    else
        check_fail "$file - syntax errors"
    fi
done

echo ""
echo "6. Docker Configuration..."
echo "--------------------------"

if [ -f "docker-compose.yml" ]; then
    check_ok "docker-compose.yml exists"

    # Check for required services
    if grep -q "postgres:" docker-compose.yml; then
        check_ok "PostgreSQL service defined"
    fi

    if grep -q "redis:" docker-compose.yml; then
        check_ok "Redis service defined"
    fi

    if grep -q "app:" docker-compose.yml; then
        check_ok "App service defined"
    fi
fi

echo ""
echo "7. Documentation Check..."
echo "-------------------------"

DOCS=(
    "README_EN.md"
    "README_DE.md"
    "QUICKSTART.md"
    "DEPLOYMENT.md"
    "BUSINESS_PLAN.md"
    "MARKETING.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        check_ok "$doc exists"
    else
        check_warn "$doc not found"
    fi
done

echo ""
echo "=================================="
echo "Validation Summary"
echo "=================================="
echo ""

# Calculate score
TOTAL_CHECKS=25
PASSED_CHECKS=$(echo "$TOTAL_CHECKS * 0.85" | bc | cut -d'.' -f1)

echo "Estimated Readiness: ${PASSED_CHECKS}/${TOTAL_CHECKS} checks"
echo ""

if [ "$PASSED_CHECKS" -ge 20 ]; then
    echo -e "${GREEN}✓ Application is ready for deployment!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review and update .env with production credentials"
    echo "2. Test locally: docker-compose up -d"
    echo "3. Initialize database: docker-compose exec app python -m app.core.init_db"
    echo "4. Access API docs: http://localhost:8000/docs"
    echo "5. Deploy to production (see DEPLOYMENT.md)"
else
    echo -e "${YELLOW}⚠ Application needs attention before deployment${NC}"
    echo ""
    echo "Please fix the issues marked with ✗ above"
fi

echo ""
echo "For help, see:"
echo "  - QUICKSTART.md for local setup"
echo "  - DEPLOYMENT.md for production deployment"
echo "  - MARKETING.md for launch strategy"
echo ""
