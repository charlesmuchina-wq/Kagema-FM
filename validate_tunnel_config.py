#!/usr/bin/env python3
"""
Tunnel Configuration Validator
Ensures all tunnel-related configurations are consistent and use Emergent tunnels
"""

import os
import json
from pathlib import Path

def validate_tunnel_config():
    """Validate tunnel configuration consistency"""
    issues = []
    
    # Check frontend .env
    frontend_env = Path('/app/frontend/.env')
    if frontend_env.exists():
        with open(frontend_env) as f:
            env_content = f.read()
            
        if 'localhost:4040' in env_content:
            issues.append("Legacy ngrok reference in frontend/.env")
        
        if 'carmedia-hub-1.preview.emergentagent.com' not in env_content:
            issues.append("Missing Emergent tunnel URL in frontend/.env")
    
    # Check for running ngrok processes
    import subprocess
    try:
        result = subprocess.run(['pgrep', '-f', 'ngrok'], capture_output=True)
        if result.returncode == 0:
            issues.append("Legacy ngrok process still running")
    except:
        pass
    
    # Check supervisor configuration
    tunnel_config = Path('/etc/supervisor/conf.d/tunnel-watchdog.conf')
    if tunnel_config.exists():
        with open(tunnel_config) as f:
            config_content = f.read()
            
        # Check if it's still using old legacy script
        if 'tunnel_watchdog.sh' in config_content and 'emergent_tunnel_watchdog.sh' not in config_content:
            issues.append("Legacy tunnel watchdog in supervisor config")
        elif 'emergent_tunnel_watchdog.sh' not in config_content:
            issues.append("Emergent tunnel watchdog not configured in supervisor")
    else:
        # Check if new config exists
        emergent_config = Path('/etc/supervisor/conf.d/emergent-tunnel-watchdog.conf')  
        if not emergent_config.exists():
            issues.append("No tunnel monitoring configuration found")
    
    return issues

if __name__ == "__main__":
    issues = validate_tunnel_config()
    if issues:
        print("❌ Tunnel configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
        exit(1)
    else:
        print("✅ Tunnel configuration is valid")
        exit(0)
