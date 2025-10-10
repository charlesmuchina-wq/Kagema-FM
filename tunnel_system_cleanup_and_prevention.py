#!/usr/bin/env python3
"""
Tunnel System Cleanup and Prevention System
Comprehensive cleanup of legacy ngrok references and implementation of preventive measures
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Set
import logging
from datetime import datetime

class TunnelSystemCleanup:
    def __init__(self):
        self.app_root = Path('/app')
        self.legacy_patterns = [
            r'ngrok',
            r'localhost:4040',
            r'\.ngrok\.',
            r'ERR_NGROK',
            r'tunnel_manager\.py'
        ]
        self.emergent_patterns = [
            r'carmedia-hub-1\.preview\.emergentagent\.com',
            r'EXPO_PACKAGER_HOSTNAME',
            r'EXPO_PUBLIC_BACKEND_URL'
        ]
        
        self.cleanup_report = {
            'timestamp': datetime.now().isoformat(),
            'files_scanned': 0,
            'legacy_references_found': [],
            'cleanup_actions_taken': [],
            'preventive_measures_implemented': []
        }
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/app/tunnel_cleanup.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def scan_for_legacy_references(self) -> List[Dict]:
        """Scan all files for legacy ngrok references"""
        self.logger.info("🔍 Scanning for legacy tunnel references...")
        
        legacy_references = []
        file_types_to_scan = ['.py', '.js', '.ts', '.tsx', '.json', '.yaml', '.yml', '.sh', '.md', '.conf', '.env']
        
        # Skip certain directories
        skip_dirs = {'node_modules', '.git', '__pycache__', '.expo', '.next', 'build', 'dist'}
        
        for file_path in self.app_root.rglob('*'):
            if file_path.is_file() and file_path.suffix in file_types_to_scan:
                # Skip files in excluded directories
                if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    continue
                
                self.cleanup_report['files_scanned'] += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for line_num, line in enumerate(content.split('\n'), 1):
                        for pattern in self.legacy_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                legacy_ref = {
                                    'file': str(file_path),
                                    'line_number': line_num,
                                    'pattern': pattern,
                                    'content': line.strip(),
                                    'severity': self._assess_severity(pattern, line)
                                }
                                legacy_references.append(legacy_ref)
                                
                except Exception as e:
                    self.logger.warning(f"Could not scan {file_path}: {e}")
        
        self.cleanup_report['legacy_references_found'] = legacy_references
        return legacy_references
    
    def _assess_severity(self, pattern: str, line: str) -> str:
        """Assess the severity of a legacy reference"""
        if 'localhost:4040' in line or 'ngrok' in line.lower():
            return 'HIGH'
        elif 'tunnel_manager' in line:
            return 'MEDIUM'
        elif 'ERR_NGROK' in line:
            return 'LOW'  # Just error messages
        else:
            return 'INFO'
    
    def clean_legacy_references(self, legacy_references: List[Dict]) -> None:
        """Clean up legacy references based on severity"""
        self.logger.info("🧹 Starting legacy reference cleanup...")
        
        high_priority_files = set()
        medium_priority_files = set()
        
        # Group files by severity
        for ref in legacy_references:
            if ref['severity'] == 'HIGH':
                high_priority_files.add(ref['file'])
            elif ref['severity'] == 'MEDIUM':
                medium_priority_files.add(ref['file'])
        
        # Handle high priority files
        for file_path in high_priority_files:
            self._clean_file(file_path, 'HIGH')
        
        # Handle medium priority files
        for file_path in medium_priority_files:
            self._clean_file(file_path, 'MEDIUM')
    
    def _clean_file(self, file_path: str, severity: str) -> None:
        """Clean a specific file of legacy references"""
        try:
            # Skip if it's our new tunnel system files
            if 'emergent_tunnel_watchdog' in file_path or 'tunnel_system_cleanup' in file_path:
                return
            
            # Special handling for different file types
            if file_path.endswith('.sh') and 'tunnel_watchdog.sh' in file_path:
                self._archive_legacy_script(file_path)
            elif file_path.endswith('.py') and 'tunnel_manager.py' in file_path:
                self._archive_legacy_script(file_path)
            elif file_path.endswith('.md'):
                self._update_documentation(file_path)
            else:
                self.logger.info(f"📝 Marked for review: {file_path} (severity: {severity})")
                
        except Exception as e:
            self.logger.error(f"Error cleaning {file_path}: {e}")
    
    def _archive_legacy_script(self, file_path: str) -> None:
        """Archive legacy scripts instead of deleting"""
        archive_path = f"{file_path}.legacy_archived_{datetime.now().strftime('%Y%m%d')}"
        
        try:
            subprocess.run(['mv', file_path, archive_path], check=True)
            self.logger.info(f"📦 Archived legacy script: {file_path} -> {archive_path}")
            self.cleanup_report['cleanup_actions_taken'].append({
                'action': 'archived',
                'file': file_path,
                'new_location': archive_path
            })
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to archive {file_path}: {e}")
    
    def _update_documentation(self, file_path: str) -> None:
        """Update documentation to reflect new tunnel system"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Add deprecation notice for ngrok references
            if 'ngrok' in content.lower():
                deprecation_notice = """
## 🚨 DEPRECATION NOTICE
**Legacy ngrok references in this document are deprecated.**
**Current tunnel system**: Emergent Platform Tunnels (https://carmedia-hub-1.preview.emergentagent.com)
**For current tunnel information**, see: /app/emergent_tunnel_watchdog.sh

---

"""
                # Add notice at the beginning
                updated_content = deprecation_notice + content
                
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                
                self.logger.info(f"📚 Updated documentation: {file_path}")
                self.cleanup_report['cleanup_actions_taken'].append({
                    'action': 'documentation_updated',
                    'file': file_path,
                    'change': 'Added deprecation notice'
                })
                
        except Exception as e:
            self.logger.error(f"Error updating documentation {file_path}: {e}")
    
    def implement_preventive_measures(self) -> None:
        """Implement preventive measures to avoid future legacy reference issues"""
        self.logger.info("🛡️ Implementing preventive measures...")
        
        # 1. Create tunnel configuration validation script
        self._create_tunnel_config_validator()
        
        # 2. Create pre-commit hook for legacy detection
        self._create_pre_commit_hook()
        
        # 3. Create tunnel system documentation
        self._create_tunnel_documentation()
        
        # 4. Create health check validation
        self._create_health_check_validator()
    
    def _create_tunnel_config_validator(self) -> None:
        """Create a script to validate tunnel configuration consistency"""
        validator_script = """#!/usr/bin/env python3
\"\"\"
Tunnel Configuration Validator
Ensures all tunnel-related configurations are consistent and use Emergent tunnels
\"\"\"

import os
import json
from pathlib import Path

def validate_tunnel_config():
    \"\"\"Validate tunnel configuration consistency\"\"\"
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
            
        if 'tunnel_watchdog.sh' in config_content:
            issues.append("Legacy tunnel watchdog in supervisor config")
    
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
"""
        
        validator_path = '/app/validate_tunnel_config.py'
        with open(validator_path, 'w') as f:
            f.write(validator_script)
        os.chmod(validator_path, 0o755)
        
        self.logger.info("✅ Created tunnel configuration validator")
        self.cleanup_report['preventive_measures_implemented'].append({
            'measure': 'tunnel_config_validator',
            'file': validator_path
        })
    
    def _create_pre_commit_hook(self) -> None:
        """Create a pre-commit hook to detect legacy references"""
        hook_script = """#!/bin/bash
# Pre-commit hook to detect legacy tunnel references

echo "🔍 Checking for legacy tunnel references..."

# Check for common legacy patterns
if git diff --cached --name-only | xargs grep -l "localhost:4040\\|ngrok" 2>/dev/null; then
    echo "❌ Legacy tunnel references detected in staged files:"
    git diff --cached --name-only | xargs grep -n "localhost:4040\\|ngrok" 2>/dev/null || true
    echo ""
    echo "Please update to use Emergent tunnel URLs:"
    echo "  Current: https://carmedia-hub-1.preview.emergentagent.com"
    echo ""
    echo "To bypass this check: git commit --no-verify"
    exit 1
fi

echo "✅ No legacy tunnel references found"
exit 0
"""
        
        hooks_dir = Path('/app/.git/hooks')
        if hooks_dir.exists():
            hook_path = hooks_dir / 'pre-commit'
            with open(hook_path, 'w') as f:
                f.write(hook_script)
            os.chmod(hook_path, 0o755)
            
            self.logger.info("✅ Created pre-commit hook for legacy detection")
            self.cleanup_report['preventive_measures_implemented'].append({
                'measure': 'pre_commit_hook',
                'file': str(hook_path)
            })
    
    def _create_tunnel_documentation(self) -> None:
        """Create comprehensive tunnel system documentation"""
        docs_content = """# Tunnel System Architecture - Kagema FM

## Current Tunnel System

### Emergent Platform Tunnels ✅
- **Primary URL**: https://carmedia-hub-1.preview.emergentagent.com
- **Backend API**: https://carmedia-hub-1.preview.emergentagent.com/api/
- **Frontend**: https://carmedia-hub-1.preview.emergentagent.com/
- **Monitoring**: /app/emergent_tunnel_watchdog.sh

### Configuration Files
- **Frontend Environment**: `/app/frontend/.env`
- **Supervisor Config**: `/etc/supervisor/conf.d/tunnel-watchdog.conf`
- **Monitoring Script**: `/app/emergent_tunnel_watchdog.sh`

## Legacy System (DEPRECATED) ❌

### ngrok (No longer used)
- **Legacy URL Pattern**: localhost:4040/api/tunnels
- **Legacy Scripts**: tunnel_watchdog.sh, tunnel_manager.py
- **Status**: Archived and replaced

## Troubleshooting

### Common Issues
1. **ERR_NGROK_3200**: Legacy reference issue
   - **Solution**: Ensure all configurations use Emergent tunnel URLs
   - **Validation**: Run `/app/validate_tunnel_config.py`

2. **Tunnel Health Check Failures**
   - **Check**: Monitor `/var/log/emergent_tunnel_watchdog.log`
   - **Commands**: `supervisorctl status emergent-tunnel-watchdog`

3. **Configuration Validation**
   - **Script**: `/app/validate_tunnel_config.py`
   - **Manual Check**: Verify .env files use correct URLs

### Health Monitoring
- **Watchdog Process**: `emergent-tunnel-watchdog`
- **Health Check Interval**: 60 seconds
- **Performance Check Interval**: 300 seconds (5 minutes)
- **Log Location**: `/var/log/emergent_tunnel_watchdog.log`

### Emergency Procedures
1. **Tunnel Failure Recovery**:
   ```bash
   supervisorctl restart emergent-tunnel-watchdog
   supervisorctl restart expo
   ```

2. **Configuration Reset**:
   ```bash
   /app/validate_tunnel_config.py
   supervisorctl reread
   supervisorctl update
   ```

3. **Legacy Cleanup**:
   ```bash
   /app/tunnel_system_cleanup_and_prevention.py
   ```

---
*Last Updated: {timestamp}*
*System Version: Emergent Platform Integration*
""".format(timestamp=datetime.now().isoformat())
        
        docs_path = '/app/TUNNEL_SYSTEM_DOCS.md'
        with open(docs_path, 'w') as f:
            f.write(docs_content)
        
        self.logger.info("📚 Created tunnel system documentation")
        self.cleanup_report['preventive_measures_implemented'].append({
            'measure': 'tunnel_documentation',
            'file': docs_path
        })
    
    def _create_health_check_validator(self) -> None:
        """Create a comprehensive health check validator"""
        validator_script = """#!/usr/bin/env python3
\"\"\"
Comprehensive Tunnel Health Validator
\"\"\"

import requests
import subprocess
import sys
from datetime import datetime

def check_emergent_tunnel_health():
    \"\"\"Check Emergent tunnel system health\"\"\"
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
"""
        
        validator_path = '/app/check_tunnel_health.py'
        with open(validator_path, 'w') as f:
            f.write(validator_script)
        os.chmod(validator_path, 0o755)
        
        self.logger.info("✅ Created health check validator")
        self.cleanup_report['preventive_measures_implemented'].append({
            'measure': 'health_check_validator',
            'file': validator_path
        })
    
    def generate_cleanup_report(self) -> str:
        """Generate comprehensive cleanup report"""
        report_path = f'/app/tunnel_cleanup_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(report_path, 'w') as f:
            json.dump(self.cleanup_report, f, indent=2)
        
        return report_path
    
    def run_complete_cleanup_and_prevention(self) -> Dict:
        """Run the complete cleanup and prevention process"""
        self.logger.info("🚀 Starting comprehensive tunnel system cleanup and prevention")
        
        # Phase 1: Scan for legacy references
        legacy_refs = self.scan_for_legacy_references()
        self.logger.info(f"📊 Found {len(legacy_refs)} legacy references in {self.cleanup_report['files_scanned']} files")
        
        # Phase 2: Clean up legacy references
        if legacy_refs:
            self.clean_legacy_references(legacy_refs)
        
        # Phase 3: Implement preventive measures
        self.implement_preventive_measures()
        
        # Phase 4: Generate report
        report_path = self.generate_cleanup_report()
        self.logger.info(f"📄 Cleanup report generated: {report_path}")
        
        # Phase 5: Final validation
        try:
            subprocess.run(['/app/validate_tunnel_config.py'], check=True)
            self.logger.info("✅ Final validation successful")
        except subprocess.CalledProcessError:
            self.logger.warning("⚠️ Final validation found issues - review required")
        
        return {
            'status': 'COMPLETE',
            'legacy_references_found': len(legacy_refs),
            'cleanup_actions_taken': len(self.cleanup_report['cleanup_actions_taken']),
            'preventive_measures_implemented': len(self.cleanup_report['preventive_measures_implemented']),
            'report_path': report_path
        }

if __name__ == "__main__":
    cleanup_system = TunnelSystemCleanup()
    results = cleanup_system.run_complete_cleanup_and_prevention()
    
    print("=" * 80)
    print("🎉 TUNNEL SYSTEM CLEANUP AND PREVENTION COMPLETE")
    print("=" * 80)
    print(f"Status: {results['status']}")
    print(f"Legacy References Found: {results['legacy_references_found']}")
    print(f"Cleanup Actions Taken: {results['cleanup_actions_taken']}")  
    print(f"Preventive Measures Implemented: {results['preventive_measures_implemented']}")
    print(f"Report Location: {results['report_path']}")
    print("=" * 80)