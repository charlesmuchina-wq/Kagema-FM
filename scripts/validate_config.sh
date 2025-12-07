#!/bin/bash

# Dragon KARAU AI - Configuration Validation Script
# Validates all critical configuration files before deployment

set -e

COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_NC='\033[0m' # No Color

FAILED_CHECKS=0

log_success() {
    echo -e "${COLOR_GREEN}✓${COLOR_NC} $1"
}

log_error() {
    echo -e "${COLOR_RED}✗${COLOR_NC} $1"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
}

log_warning() {
    echo -e "${COLOR_YELLOW}⚠${COLOR_NC} $1"
}

echo "========================================="
echo "Dragon KARAU AI - Configuration Validation"
echo "========================================="
echo ""

# Check 1: Frontend .env file
echo "Checking frontend environment variables..."
if [ -f "/app/frontend/.env" ]; then
    ENV_FILE="/app/frontend/.env"
    
    # Required variables
    REQUIRED_VARS=("EXPO_PUBLIC_BACKEND_URL" "EXPO_PACKAGER_PROXY_URL" "EXPO_PACKAGER_HOSTNAME")
    
    for VAR in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${VAR}=" "$ENV_FILE"; then
            VALUE=$(grep "^${VAR}=" "$ENV_FILE" | cut -d '=' -f2)
            if [ ! -z "$VALUE" ]; then
                log_success "Frontend env var '$VAR' is set"
            else
                log_error "Frontend env var '$VAR' is empty"
            fi
        else
            log_error "Frontend env var '$VAR' is missing"
        fi
    done
else
    log_error "Frontend .env file not found"
fi

echo ""

# Check 2: Backend .env file
echo "Checking backend environment variables..."
if [ -f "/app/backend/.env" ]; then
    ENV_FILE="/app/backend/.env"
    
    # Required variables
    if grep -q "^MONGO_URL=" "$ENV_FILE"; then
        log_success "Backend MONGO_URL is configured"
    else
        log_error "Backend MONGO_URL is missing"
    fi
else
    log_error "Backend .env file not found"
fi

echo ""

# Check 3: Metro config
echo "Checking Metro bundler configuration..."
if [ -f "/app/frontend/metro.config.js" ]; then
    METRO_CONFIG="/app/frontend/metro.config.js"
    
    # Check for font file extensions
    if grep -q "ttf.*otf\|otf.*ttf" "$METRO_CONFIG"; then
        log_success "Metro config includes font file extensions"
    else
        log_warning "Metro config may be missing font extensions (ttf, otf)"
    fi
    
    # Check for asset extensions configuration
    if grep -q "assetExts" "$METRO_CONFIG"; then
        log_success "Metro config has assetExts configured"
    else
        log_error "Metro config missing assetExts configuration"
    fi
else
    log_error "Metro config file not found"
fi

echo ""

# Check 4: Babel config
echo "Checking Babel configuration..."
if [ -f "/app/frontend/babel.config.js" ]; then
    log_success "Babel config exists"
    
    BABEL_CONFIG="/app/frontend/babel.config.js"
    
    # Check for module resolver
    if grep -q "babel-plugin-module-resolver" "$BABEL_CONFIG"; then
        log_success "Babel config includes module resolver plugin"
    else
        log_warning "Babel config may be missing module resolver"
    fi
else
    log_error "Babel config file not found"
fi

echo ""

# Check 5: Package.json
echo "Checking package.json..."
if [ -f "/app/frontend/package.json" ]; then
    PKG_JSON="/app/frontend/package.json"
    
    # Check critical dependencies
    REQUIRED_DEPS=("expo" "expo-router" "@expo/vector-icons" "react-native")
    
    for DEP in "${REQUIRED_DEPS[@]}"; do
        if grep -q "\"${DEP}\"" "$PKG_JSON"; then
            log_success "Dependency '$DEP' is present"
        else
            log_error "Dependency '$DEP' is missing"
        fi
    done
else
    log_error "Frontend package.json not found"
fi

echo ""

# Check 6: Root layout file
echo "Checking root layout configuration..."
if [ -f "/app/frontend/app/_layout.tsx" ]; then
    LAYOUT_FILE="/app/frontend/app/_layout.tsx"
    
    # Check for font loading
    if grep -q "useFonts" "$LAYOUT_FILE"; then
        log_success "Root layout includes font loading"
    else
        log_warning "Root layout may be missing font preloading"
    fi
    
    # Check for Ionicons
    if grep -q "Ionicons" "$LAYOUT_FILE"; then
        log_success "Root layout includes Ionicons import"
    else
        log_warning "Root layout may be missing Ionicons"
    fi
else
    log_error "Root layout file not found"
fi

echo ""

# Check 7: Services status
echo "Checking services status..."
SERVICES=("expo" "backend" "mongodb")

for SERVICE in "${SERVICES[@]}"; do
    STATUS=$(sudo supervisorctl status "$SERVICE" 2>&1)
    
    if echo "$STATUS" | grep -q "RUNNING"; then
        log_success "Service '$SERVICE' is running"
    else
        log_error "Service '$SERVICE' is NOT running"
    fi
done

echo ""

# Check 8: Port availability
echo "Checking port availability..."
if netstat -tuln | grep -q ":3000 "; then
    log_success "Port 3000 is in use (frontend)"
else
    log_warning "Port 3000 is not in use (frontend may not be running)"
fi

if netstat -tuln | grep -q ":8001 "; then
    log_success "Port 8001 is in use (backend)"
else
    log_warning "Port 8001 is not in use (backend may not be running)"
fi

echo ""

# Check 9: Design tokens
echo "Checking design system..."
if [ -f "/app/frontend/constants/designTokens.ts" ]; then
    log_success "Design tokens file exists"
else
    log_warning "Design tokens file not found (optional)"
fi

echo ""

# Final summary
echo "========================================="
echo "Validation Summary"
echo "========================================="

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${COLOR_GREEN}✓ All critical checks passed!${COLOR_NC}"
    exit 0
else
    echo -e "${COLOR_RED}✗ $FAILED_CHECKS check(s) failed${COLOR_NC}"
    echo ""
    echo "Please fix the issues above before deployment."
    exit 1
fi
