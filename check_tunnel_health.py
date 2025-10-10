#!/usr/bin/env python3
"""
Comprehensive Tunnel Health Validator
"""

import requests
import subprocess
import sys
from datetime import datetime

def check_emergent_tunnel_health():
    """Check Emergent tunnel system health"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'UNKNOWN',
        'checks': {}
    }
    
    base_url = "https://carmedia-hub-1.preview.emergentagent.com"
    
    # Test backend
    try:
        response = requests.get(f"{base_url}/api/", timeout=10)
        results['checks']['backend'] = {
            'status': 'HEALTHY' if response.status_code == 200 else 'UNHEALTHY',
            'response_code': response.status_code,
            'response_time': response.elapsed.total_seconds()
        }
    except Exception as e:
        results['checks']['backend'] = {
            'status': 'ERROR',
            'error': str(e)
        }
    
    # Test frontend
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        results['checks']['frontend'] = {
            'status': 'HEALTHY' if response.status_code == 200 else 'UNHEALTHY',
            'response_code': response.status_code,
            'response_time': response.elapsed.total_seconds()
        }
    except Exception as e:
        results['checks']['frontend'] = {
            'status': 'ERROR',
            'error': str(e)
        }
    
    # Check watchdog process
    try:
        result = subprocess.run(['supervisorctl', 'status', 'emergent-tunnel-watchdog'], 
                              capture_output=True, text=True)
        if 'RUNNING' in result.stdout:
            results['checks']['watchdog'] = {'status': 'RUNNING'}
        else:
            results['checks']['watchdog'] = {'status': 'NOT_RUNNING', 'output': result.stdout}
    except Exception as e:
        results['checks']['watchdog'] = {'status': 'ERROR', 'error': str(e)}
    
    # Determine overall status
    all_healthy = all(
        check.get('status') in ['HEALTHY', 'RUNNING'] 
        for check in results['checks'].values()
    )
    
    results['overall_status'] = 'HEALTHY' if all_healthy else 'DEGRADED'
    
    return results

if __name__ == "__main__":
    results = check_emergent_tunnel_health()
    
    print(f"🔍 Tunnel Health Check - {results['timestamp']}")
    print(f"📊 Overall Status: {results['overall_status']}")
    print("")
    
    for component, check in results['checks'].items():
        status_emoji = "✅" if check['status'] in ['HEALTHY', 'RUNNING'] else "❌"
        print(f"{status_emoji} {component.title()}: {check['status']}")
        
        if 'response_time' in check:
            print(f"   Response Time: {check['response_time']:.3f}s")
        if 'error' in check:
            print(f"   Error: {check['error']}")
    
    sys.exit(0 if results['overall_status'] == 'HEALTHY' else 1)
