#!/bin/bash

# Comprehensive Tunnel Manager - Ngrok Alternative
# Supports cloudflared, localtunnel, and direct port forwarding

FRONTEND_PORT=3000
BACKEND_PORT=8001
TUNNEL_TYPE="cloudflared"  # Options: cloudflared, localtunnel, direct
LOG_FILE="/var/log/tunnel-manager.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Stop existing tunnels
stop_tunnels() {
    log "🛑 Stopping existing tunnels..."
    pkill -f "cloudflared tunnel"
    pkill -f "ngrok"
    pkill -f "lt --port"
    killall cloudflared 2>/dev/null
}

# Start Cloudflared Tunnel (Preferred alternative to ngrok)
start_cloudflared() {
    log "🌐 Starting Cloudflared tunnels..."
    
    # Check if cloudflared is available
    if ! command -v cloudflared &> /dev/null; then
        log "❌ Cloudflared not found. Installing..."
        install_cloudflared
    fi
    
    # Start frontend tunnel
    cloudflared tunnel --url http://localhost:$FRONTEND_PORT --no-autoupdate &
    FRONTEND_PID=$!
    sleep 3
    
    # Start backend tunnel  
    cloudflared tunnel --url http://localhost:$BACKEND_PORT --no-autoupdate &
    BACKEND_PID=$!
    sleep 3
    
    # Get tunnel URLs
    FRONTEND_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url' 2>/dev/null || echo "")
    if [ -z "$FRONTEND_URL" ]; then
        FRONTEND_URL="https://$(curl -s localhost:4040/api/tunnels | grep -o '[a-z0-9]*\.trycloudflare\.com' | head -1)"
    fi
    
    log "✅ Cloudflared tunnels started:"
    log "   Frontend: $FRONTEND_URL"
    log "   Backend: Available via same tunnel on /api/*"
    
    # Update environment files
    update_env_files "$FRONTEND_URL"
    
    return 0
}

# Install Cloudflared
install_cloudflared() {
    log "📦 Installing Cloudflared..."
    
    # Detect architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" == "x86_64" ]]; then
        ARCH="amd64"
    elif [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
        ARCH="arm64"
    else
        log "❌ Unsupported architecture: $ARCH"
        return 1
    fi
    
    # Download and install
    curl -L --output cloudflared "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-$ARCH"
    chmod +x cloudflared
    sudo mv cloudflared /usr/local/bin/
    
    log "✅ Cloudflared installed successfully"
}

# Start Localtunnel (Backup alternative)
start_localtunnel() {
    log "🚇 Starting Localtunnel..."
    
    # Install localtunnel if not available
    if ! command -v lt &> /dev/null; then
        log "📦 Installing Localtunnel..."
        npm install -g localtunnel
    fi
    
    # Start tunnels
    lt --port $FRONTEND_PORT --subdomain kagema-fm-frontend &
    FRONTEND_LT_PID=$!
    sleep 2
    
    lt --port $BACKEND_PORT --subdomain kagema-fm-backend &
    BACKEND_LT_PID=$!
    sleep 2
    
    FRONTEND_URL="https://kagema-fm-frontend.loca.lt"
    BACKEND_URL="https://kagema-fm-backend.loca.lt"
    
    log "✅ Localtunnel started:"
    log "   Frontend: $FRONTEND_URL"
    log "   Backend: $BACKEND_URL"
    
    # Update environment files
    update_env_files "$FRONTEND_URL"
    
    return 0
}

# Direct port forwarding (No tunnel)
start_direct() {
    log "🔗 Using direct port forwarding..."
    
    FRONTEND_URL="http://localhost:$FRONTEND_PORT"
    BACKEND_URL="http://localhost:$BACKEND_PORT"
    
    log "✅ Direct access configured:"
    log "   Frontend: $FRONTEND_URL"
    log "   Backend: $BACKEND_URL"
    
    # Update environment files for localhost
    update_env_files "$FRONTEND_URL"
    
    return 0
}

# Update environment files with tunnel URLs
update_env_files() {
    local FRONTEND_URL=$1
    
    log "📝 Updating environment files..."
    
    # Update frontend .env
    if [ -f "/app/frontend/.env" ]; then
        # Preserve existing variables and update tunnel URL
        sed -i "s|EXPO_PACKAGER_HOSTNAME=.*|EXPO_PACKAGER_HOSTNAME=${FRONTEND_URL#*://}|g" /app/frontend/.env
        sed -i "s|EXPO_PACKAGER_PROXY_URL=.*|EXPO_PACKAGER_PROXY_URL=$FRONTEND_URL|g" /app/frontend/.env
        log "   ✅ Frontend .env updated"
    fi
    
    # Update backend .env if needed
    if [ -f "/app/backend/.env" ]; then
        log "   ✅ Backend .env maintained"
    fi
}

# Health check for tunnels
health_check() {
    log "🔍 Performing tunnel health check..."
    
    # Check frontend
    if curl -s --max-time 5 "http://localhost:$FRONTEND_PORT" >/dev/null; then
        log "   ✅ Frontend service responsive"
    else
        log "   ❌ Frontend service not responding"
        return 1
    fi
    
    # Check backend
    if curl -s --max-time 5 "http://localhost:$BACKEND_PORT/api/" >/dev/null; then
        log "   ✅ Backend service responsive"
    else
        log "   ❌ Backend service not responding"
        return 1
    fi
    
    return 0
}

# Monitor and restart if needed
monitor_tunnels() {
    log "👀 Starting tunnel monitoring..."
    
    while true; do
        sleep 30
        
        if ! health_check; then
            log "⚠️ Tunnel health check failed, restarting..."
            start_tunnels
        fi
    done
}

# Main function to start tunnels
start_tunnels() {
    stop_tunnels
    sleep 2
    
    case "$TUNNEL_TYPE" in
        "cloudflared")
            start_cloudflared
            ;;
        "localtunnel")
            start_localtunnel
            ;;
        "direct")
            start_direct
            ;;
        *)
            log "❌ Unknown tunnel type: $TUNNEL_TYPE"
            return 1
            ;;
    esac
    
    # Wait for services to start
    sleep 5
    
    # Perform initial health check
    if health_check; then
        log "✅ All tunnels started successfully"
    else
        log "⚠️ Some services not responding, but tunnels are active"
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [start|stop|restart|status|monitor]"
    echo ""
    echo "Commands:"
    echo "  start    - Start tunnel services"
    echo "  stop     - Stop all tunnels"
    echo "  restart  - Restart tunnels"
    echo "  status   - Check tunnel status"
    echo "  monitor  - Start with monitoring"
    echo ""
    echo "Environment Variables:"
    echo "  TUNNEL_TYPE=cloudflared|localtunnel|direct (default: cloudflared)"
}

# Main script logic
case "${1:-start}" in
    "start")
        log "🚀 Starting Kagema FM tunnel manager..."
        start_tunnels
        ;;
    "stop")
        log "🛑 Stopping all tunnels..."
        stop_tunnels
        ;;
    "restart")
        log "🔄 Restarting tunnels..."
        start_tunnels
        ;;
    "status")
        health_check && echo "✅ Tunnels healthy" || echo "❌ Tunnel issues detected"
        ;;
    "monitor")
        start_tunnels
        monitor_tunnels
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

log "✅ Tunnel manager operation completed"