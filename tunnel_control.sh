#!/bin/bash
"""
Kagema FM Tunnel Control Script
Convenient management interface for tunnel operations
"""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUNNEL_MANAGER="$SCRIPT_DIR/tunnel_manager.py"
LOG_FILE="/var/log/tunnel_manager.log"

show_help() {
    echo "Kagema FM Tunnel Control"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  status      Show current tunnel status"
    echo "  restart     Force restart tunnel service"
    echo "  recover     Run auto-recovery process"
    echo "  monitor     Start continuous monitoring (foreground)"
    echo "  logs        Show tunnel manager logs"
    echo "  watchdog    Show watchdog logs"
    echo "  test        Test tunnel connectivity"
    echo "  info        Show detailed tunnel information"
    echo "  kill        Emergency: kill all ngrok processes"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status       # Quick status check"
    echo "  $0 restart      # Force restart if having issues"
    echo "  $0 test         # Test if tunnels are accessible"
}

show_status() {
    echo "🔍 Checking tunnel status..."
    
    # Check if ngrok API is accessible
    if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
        echo "✅ Ngrok API accessible"
        
        # Get tunnel information
        local tunnels=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[] | "\(.proto): \(.public_url)"' 2>/dev/null)
        
        if [[ -n "$tunnels" ]]; then
            echo "📡 Active tunnels:"
            echo "$tunnels" | sed 's/^/  /'
        else
            echo "⚠️ No active tunnels found"
        fi
    else
        echo "❌ Ngrok API not accessible"
    fi
    
    # Check supervisor services
    echo ""
    echo "🔧 Service status:"
    supervisorctl status expo tunnel-watchdog | sed 's/^/  /'
}

test_connectivity() {
    echo "🧪 Testing tunnel connectivity..."
    
    local tunnel_url=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[] | select(.proto=="https") | .public_url' 2>/dev/null | head -1)
    
    if [[ -n "$tunnel_url" ]] && [[ "$tunnel_url" != "null" ]]; then
        echo "🌐 Testing: $tunnel_url"
        
        if curl -s --max-time 10 "$tunnel_url" > /dev/null 2>&1; then
            echo "✅ Tunnel is accessible"
            echo "🔗 URL: $tunnel_url"
        else
            echo "❌ Tunnel exists but not accessible"
            echo "🔗 URL: $tunnel_url"
        fi
    else
        echo "❌ No HTTPS tunnel found"
    fi
}

show_detailed_info() {
    echo "📊 Detailed tunnel information:"
    echo ""
    
    # Tunnel API response
    local api_response=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        echo "🔌 Tunnel API Response:"
        echo "$api_response" | jq . 2>/dev/null || echo "$api_response"
    else
        echo "❌ Failed to get tunnel API response"
    fi
    
    echo ""
    echo "🔄 Process information:"
    ps aux | grep -E "(ngrok|expo)" | grep -v grep | sed 's/^/  /'
    
    echo ""
    echo "📝 Recent tunnel manager activity:"
    if [[ -f "$LOG_FILE" ]]; then
        tail -10 "$LOG_FILE" | sed 's/^/  /'
    else
        echo "  No log file found"
    fi
}

restart_tunnel() {
    echo "🔄 Restarting tunnel service..."
    
    # Stop services
    supervisorctl stop expo
    sleep 2
    
    # Kill ngrok processes
    pkill -f ngrok 2>/dev/null
    sleep 1
    
    # Start services
    supervisorctl start expo
    
    echo "⏳ Waiting for tunnel to be ready..."
    sleep 5
    
    # Check if successful
    test_connectivity
}

emergency_kill() {
    echo "🚨 Emergency: Killing all ngrok processes..."
    
    # Kill all ngrok processes
    pkill -9 -f ngrok 2>/dev/null
    
    # Show remaining processes
    local remaining=$(ps aux | grep ngrok | grep -v grep)
    if [[ -n "$remaining" ]]; then
        echo "⚠️ Some processes might still be running:"
        echo "$remaining" | sed 's/^/  /'
    else
        echo "✅ All ngrok processes killed"
    fi
}

show_logs() {
    echo "📋 Tunnel Manager logs:"
    if [[ -f "$LOG_FILE" ]]; then
        tail -20 "$LOG_FILE"
    else
        echo "No tunnel manager logs found"
    fi
}

show_watchdog_logs() {
    echo "👮 Tunnel Watchdog logs:"
    if [[ -f "/var/log/tunnel_watchdog.log" ]]; then
        tail -20 "/var/log/tunnel_watchdog.log"
    else
        echo "No watchdog logs found"
    fi
}

run_recovery() {
    echo "🚑 Running auto-recovery..."
    python3 "$TUNNEL_MANAGER" --command=recover
}

start_monitor() {
    echo "👁️ Starting continuous monitoring (Ctrl+C to stop)..."
    python3 "$TUNNEL_MANAGER" --command=monitor
}

# Main command handling
case "${1:-help}" in
    status|s)
        show_status
        ;;
    restart|r)
        restart_tunnel
        ;;
    recover)
        run_recovery
        ;;
    monitor|m)
        start_monitor
        ;;
    test|t)
        test_connectivity
        ;;
    info|i)
        show_detailed_info
        ;;
    logs|l)
        show_logs
        ;;
    watchdog|w)
        show_watchdog_logs
        ;;
    kill|emergency)
        emergency_kill
        ;;
    help|h|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Run '$0 help' for available commands."
        exit 1
        ;;
esac