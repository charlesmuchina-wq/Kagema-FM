#!/usr/bin/env python3
"""
ERR_NGROK_3200 Comprehensive Resolution Validation Suite
Complete testing to validate that ERR_NGROK_3200 issue has been completely resolved
and all corrective/preventive actions are effective.
"""

import requests
import subprocess
import time
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import concurrent.futures
import threading

class ERRNgrok3200ComprehensiveValidator:
    def __init__(self):
        self.base_url = "https://carmedia-hub-1.preview.emergentagent.com"
        self.api_base = f"{self.base_url}/api"
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'validation_summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'error_resolution_status': 'UNKNOWN',
                'production_ready': False
            },
            'validation_categories': {}
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ERR_NGROK_3200_Validator/1.0',
            'Accept': 'application/json'
        })
        
    def log_test(self, message: str, status: str = "INFO"):
        """Log test progress with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_emoji = {
            "INFO": "ℹ️",
            "PASS": "✅", 
            "FAIL": "❌",
            "WARN": "⚠️"
        }.get(status, "ℹ️")
        print(f"[{timestamp}] {status_emoji} {message}")

    def validate_ngrok_error_resolution(self) -> Dict:
        """1. ERR_NGROK_3200 Resolution Validation"""
        self.log_test("Testing ERR_NGROK_3200 resolution validation...", "INFO")
        
        tests = {
            'no_ngrok_errors_in_logs': self._test_no_ngrok_errors_in_logs(),
            'tunnel_system_stability': self._test_tunnel_system_stability(),
            'api_connectivity_through_emergent': self._test_api_connectivity_through_emergent(),
            'frontend_access_through_emergent': self._test_frontend_access_through_emergent()
        }
        
        category_result = {
            'category': 'ERR_NGROK_3200 Resolution Validation',
            'total_tests': len(tests),
            'passed_tests': sum(1 for result in tests.values() if result['status'] == 'PASS'),
            'tests': tests
        }
        
        self.test_results['validation_categories']['ngrok_error_resolution'] = category_result
        return category_result

    def validate_corrective_actions(self) -> Dict:
        """2. Corrective Actions Effectiveness"""
        self.log_test("Testing corrective actions effectiveness...", "INFO")
        
        tests = {
            'legacy_system_removal': self._test_legacy_system_removal(),
            'emergent_monitoring_system': self._test_emergent_monitoring_system(),
            'configuration_consistency': self._test_configuration_consistency(),
            'service_health_validation': self._test_service_health_validation()
        }
        
        category_result = {
            'category': 'Corrective Actions Effectiveness',
            'total_tests': len(tests),
            'passed_tests': sum(1 for result in tests.values() if result['status'] == 'PASS'),
            'tests': tests
        }
        
        self.test_results['validation_categories']['corrective_actions'] = category_result
        return category_result

    def validate_preventive_actions(self) -> Dict:
        """3. Preventive Actions Effectiveness"""
        self.log_test("Testing preventive actions effectiveness...", "INFO")
        
        tests = {
            'automated_validation': self._test_automated_validation(),
            'monitoring_stability': self._test_monitoring_stability(),
            'error_prevention': self._test_error_prevention(),
            'health_check_systems': self._test_health_check_systems()
        }
        
        category_result = {
            'category': 'Preventive Actions Effectiveness',
            'total_tests': len(tests),
            'passed_tests': sum(1 for result in tests.values() if result['status'] == 'PASS'),
            'tests': tests
        }
        
        self.test_results['validation_categories']['preventive_actions'] = category_result
        return category_result

    def validate_system_performance_under_load(self) -> Dict:
        """4. System Performance Under Load"""
        self.log_test("Testing system performance under load...", "INFO")
        
        tests = {
            'api_response_times': self._test_api_response_times(),
            'concurrent_request_handling': self._test_concurrent_request_handling(),
            'tunnel_reliability': self._test_tunnel_reliability(),
            'sustained_load_performance': self._test_sustained_load_performance()
        }
        
        category_result = {
            'category': 'System Performance Under Load',
            'total_tests': len(tests),
            'passed_tests': sum(1 for result in tests.values() if result['status'] == 'PASS'),
            'tests': tests
        }
        
        self.test_results['validation_categories']['performance_under_load'] = category_result
        return category_result

    def validate_production_readiness(self) -> Dict:
        """5. Production Readiness Validation"""
        self.log_test("Testing production readiness...", "INFO")
        
        tests = {
            'all_services_running': self._test_all_services_running(),
            'no_error_conditions': self._test_no_error_conditions(),
            'documentation_complete': self._test_documentation_complete(),
            'monitoring_systems_active': self._test_monitoring_systems_active()
        }
        
        category_result = {
            'category': 'Production Readiness Validation',
            'total_tests': len(tests),
            'passed_tests': sum(1 for result in tests.values() if result['status'] == 'PASS'),
            'tests': tests
        }
        
        self.test_results['validation_categories']['production_readiness'] = category_result
        return category_result

    # Implementation of individual test methods

    def _test_no_ngrok_errors_in_logs(self) -> Dict:
        """Test that no ngrok-related errors occur in system logs"""
        try:
            # Check various log files for ngrok errors
            log_files = [
                '/var/log/supervisor/backend.err.log',
                '/var/log/supervisor/frontend.err.log', 
                '/var/log/emergent_tunnel_watchdog.log',
                '/app/monitoring.log'
            ]
            
            ngrok_errors_found = []
            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r') as f:
                            content = f.read().lower()
                            if 'err_ngrok_3200' in content or 'ngrok.*error' in content:
                                ngrok_errors_found.append(log_file)
                    except Exception:
                        continue
            
            if not ngrok_errors_found:
                return {
                    'status': 'PASS',
                    'message': 'No ngrok-related errors found in system logs',
                    'details': f'Checked {len(log_files)} log files'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Ngrok-related errors found in logs',
                    'details': f'Errors found in: {", ".join(ngrok_errors_found)}'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not check system logs',
                'details': str(e)
            }

    def _test_tunnel_system_stability(self) -> Dict:
        """Test tunnel monitoring system stability"""
        try:
            # Check if emergent tunnel watchdog is running
            result = subprocess.run(['supervisorctl', 'status', 'emergent-tunnel-watchdog'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and 'RUNNING' in result.stdout:
                # Check watchdog logs for stability
                if os.path.exists('/var/log/emergent_tunnel_watchdog.log'):
                    with open('/var/log/emergent_tunnel_watchdog.log', 'r') as f:
                        recent_logs = f.readlines()[-20:]  # Last 20 lines
                        healthy_count = sum(1 for line in recent_logs if '✅' in line)
                        error_count = sum(1 for line in recent_logs if '❌' in line)
                        
                        if healthy_count > error_count:
                            return {
                                'status': 'PASS',
                                'message': 'Tunnel monitoring system stable',
                                'details': f'Healthy: {healthy_count}, Errors: {error_count}'
                            }
                        else:
                            return {
                                'status': 'FAIL',
                                'message': 'Tunnel monitoring showing instability',
                                'details': f'Healthy: {healthy_count}, Errors: {error_count}'
                            }
                else:
                    return {
                        'status': 'WARN',
                        'message': 'Watchdog running but no logs found',
                        'details': 'Service running but log file missing'
                    }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Emergent tunnel watchdog not running',
                    'details': result.stdout.strip()
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not check tunnel system stability',
                'details': str(e)
            }

    def _test_api_connectivity_through_emergent(self) -> Dict:
        """Test all API endpoints through Emergent tunnels"""
        try:
            endpoints = [
                '/',
                '/station-info',
                '/languages',
                '/radio/streams',
                '/radio/stations',
                '/app/info',
                '/app/version'
            ]
            
            successful_endpoints = 0
            total_response_time = 0
            failed_endpoints = []
            
            for endpoint in endpoints:
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.api_base}{endpoint}", timeout=10)
                    response_time = time.time() - start_time
                    total_response_time += response_time
                    
                    if response.status_code == 200:
                        successful_endpoints += 1
                        self.log_test(f"API {endpoint}: {response.status_code} ({response_time:.3f}s)", "PASS")
                    else:
                        failed_endpoints.append(f"{endpoint}: HTTP {response.status_code}")
                        self.log_test(f"API {endpoint}: {response.status_code} ({response_time:.3f}s)", "FAIL")
                        
                except Exception as e:
                    failed_endpoints.append(f"{endpoint}: {str(e)}")
                    self.log_test(f"API {endpoint}: Error - {str(e)}", "FAIL")
            
            success_rate = (successful_endpoints / len(endpoints)) * 100
            avg_response_time = total_response_time / len(endpoints)
            
            if success_rate >= 95 and avg_response_time < 0.5:
                return {
                    'status': 'PASS',
                    'message': 'All API endpoints accessible through Emergent tunnels',
                    'details': f'Success rate: {success_rate:.1f}%, Avg response: {avg_response_time:.3f}s'
                }
            elif success_rate >= 80:
                return {
                    'status': 'WARN',
                    'message': 'Most API endpoints accessible',
                    'details': f'Success rate: {success_rate:.1f}%, Failed: {failed_endpoints}'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Multiple API endpoints failing',
                    'details': f'Success rate: {success_rate:.1f}%, Failed: {failed_endpoints}'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not test API connectivity',
                'details': str(e)
            }

    def _test_frontend_access_through_emergent(self) -> Dict:
        """Test frontend access through Emergent tunnels"""
        try:
            start_time = time.time()
            response = self.session.get(self.base_url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Check if it's actually the frontend (not just a redirect)
                content_length = len(response.content)
                if content_length > 1000:  # Frontend should have substantial content
                    return {
                        'status': 'PASS',
                        'message': 'Frontend accessible through Emergent tunnels',
                        'details': f'HTTP {response.status_code}, {response_time:.3f}s, {content_length} bytes'
                    }
                else:
                    return {
                        'status': 'WARN',
                        'message': 'Frontend accessible but content seems minimal',
                        'details': f'HTTP {response.status_code}, {content_length} bytes'
                    }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Frontend not accessible through Emergent tunnels',
                    'details': f'HTTP {response.status_code}, {response_time:.3f}s'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not test frontend access',
                'details': str(e)
            }

    def _test_legacy_system_removal(self) -> Dict:
        """Test that all legacy ngrok references have been eliminated"""
        try:
            checks = {
                'no_ngrok_processes': True,
                'no_ngrok_config_files': True,
                'legacy_files_archived': True,
                'no_ngrok_in_supervisor': True
            }
            
            # Check for ngrok processes
            result = subprocess.run(['pgrep', '-f', 'ngrok'], capture_output=True, text=True)
            if result.returncode == 0:
                checks['no_ngrok_processes'] = False
            
            # Check for ngrok config files
            ngrok_configs = ['/root/.ngrok2/ngrok.yml', '/app/.ngrok2/ngrok.yml', '/app/ngrok.yml']
            for config in ngrok_configs:
                if os.path.exists(config):
                    checks['no_ngrok_config_files'] = False
                    break
            
            # Check for archived legacy files
            legacy_files = [
                '/app/tunnel_watchdog.sh.legacy_archived_20251010',
                '/app/tunnel_manager.py.legacy_archived_20251010'
            ]
            for legacy_file in legacy_files:
                if not os.path.exists(legacy_file):
                    checks['legacy_files_archived'] = False
                    break
            
            # Check supervisor config
            result = subprocess.run(['supervisorctl', 'avail'], capture_output=True, text=True)
            if 'ngrok' in result.stdout.lower():
                checks['no_ngrok_in_supervisor'] = False
            
            passed_checks = sum(checks.values())
            total_checks = len(checks)
            
            if passed_checks == total_checks:
                return {
                    'status': 'PASS',
                    'message': 'All legacy ngrok references eliminated',
                    'details': f'All {total_checks} legacy removal checks passed'
                }
            else:
                failed_checks = [k for k, v in checks.items() if not v]
                return {
                    'status': 'FAIL',
                    'message': 'Some legacy ngrok references remain',
                    'details': f'Failed checks: {failed_checks}'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not verify legacy system removal',
                'details': str(e)
            }

    def _test_emergent_monitoring_system(self) -> Dict:
        """Test that Emergent tunnel watchdog is functioning correctly"""
        try:
            # Check if watchdog service is running
            result = subprocess.run(['supervisorctl', 'status', 'emergent-tunnel-watchdog'], 
                                  capture_output=True, text=True)
            
            if 'RUNNING' not in result.stdout:
                return {
                    'status': 'FAIL',
                    'message': 'Emergent tunnel watchdog not running',
                    'details': result.stdout.strip()
                }
            
            # Check watchdog script exists and is executable
            watchdog_script = '/app/emergent_tunnel_watchdog.sh'
            if not os.path.exists(watchdog_script):
                return {
                    'status': 'FAIL',
                    'message': 'Emergent tunnel watchdog script missing',
                    'details': f'Script not found at {watchdog_script}'
                }
            
            if not os.access(watchdog_script, os.X_OK):
                return {
                    'status': 'FAIL',
                    'message': 'Emergent tunnel watchdog script not executable',
                    'details': f'Script at {watchdog_script} lacks execute permission'
                }
            
            # Check recent watchdog activity
            log_file = '/var/log/emergent_tunnel_watchdog.log'
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    recent_logs = f.readlines()[-10:]
                    if recent_logs:
                        latest_log = recent_logs[-1]
                        if '✅' in latest_log:
                            return {
                                'status': 'PASS',
                                'message': 'Emergent tunnel watchdog functioning correctly',
                                'details': f'Service running, script executable, recent healthy status'
                            }
                        else:
                            return {
                                'status': 'WARN',
                                'message': 'Emergent tunnel watchdog running but showing issues',
                                'details': f'Latest log: {latest_log.strip()}'
                            }
                    else:
                        return {
                            'status': 'WARN',
                            'message': 'Emergent tunnel watchdog running but no recent logs',
                            'details': 'Service running but log file empty'
                        }
            else:
                return {
                    'status': 'WARN',
                    'message': 'Emergent tunnel watchdog running but no log file',
                    'details': f'Log file missing at {log_file}'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not test Emergent monitoring system',
                'details': str(e)
            }

    def _test_configuration_consistency(self) -> Dict:
        """Test that all tunnel configurations use Emergent platform URLs"""
        try:
            config_files = [
                '/app/frontend/.env',
                '/app/backend/.env'
            ]
            
            emergent_url = 'carmedia-hub-1.preview.emergentagent.com'
            config_issues = []
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        content = f.read()
                        
                        # Check for ngrok references
                        if 'ngrok' in content.lower():
                            config_issues.append(f'{config_file}: Contains ngrok references')
                        
                        # Check for Emergent URL
                        if emergent_url not in content:
                            config_issues.append(f'{config_file}: Missing Emergent URL')
                        
                        # Check for localhost references (should be minimal)
                        localhost_count = content.lower().count('localhost')
                        if localhost_count > 2:  # Allow some localhost for development
                            config_issues.append(f'{config_file}: Too many localhost references ({localhost_count})')
            
            if not config_issues:
                return {
                    'status': 'PASS',
                    'message': 'All configurations use Emergent platform URLs',
                    'details': f'Checked {len(config_files)} configuration files'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Configuration inconsistencies found',
                    'details': '; '.join(config_issues)
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not verify configuration consistency',
                'details': str(e)
            }

    def _test_service_health_validation(self) -> Dict:
        """Test service health validation systems"""
        try:
            services = ['backend', 'frontend', 'emergent-tunnel-watchdog']
            service_status = {}
            
            for service in services:
                result = subprocess.run(['supervisorctl', 'status', service], 
                                      capture_output=True, text=True)
                service_status[service] = 'RUNNING' in result.stdout
            
            running_services = sum(service_status.values())
            total_services = len(services)
            
            if running_services == total_services:
                return {
                    'status': 'PASS',
                    'message': 'All critical services running and healthy',
                    'details': f'All {total_services} services operational'
                }
            else:
                failed_services = [k for k, v in service_status.items() if not v]
                return {
                    'status': 'FAIL',
                    'message': 'Some critical services not running',
                    'details': f'Failed services: {failed_services}'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not validate service health',
                'details': str(e)
            }

    def _test_automated_validation(self) -> Dict:
        """Test configuration validators and health checkers"""
        try:
            validators = [
                '/app/validate_tunnel_config.py',
                '/app/check_tunnel_health.py'
            ]
            
            validator_results = {}
            
            for validator in validators:
                if os.path.exists(validator):
                    try:
                        result = subprocess.run(['python3', validator], 
                                              capture_output=True, text=True, timeout=30)
                        validator_results[validator] = {
                            'exists': True,
                            'executable': result.returncode == 0,
                            'output': result.stdout[:200]  # First 200 chars
                        }
                    except subprocess.TimeoutExpired:
                        validator_results[validator] = {
                            'exists': True,
                            'executable': False,
                            'output': 'Timeout'
                        }
                else:
                    validator_results[validator] = {
                        'exists': False,
                        'executable': False,
                        'output': 'File not found'
                    }
            
            working_validators = sum(1 for v in validator_results.values() if v['executable'])
            total_validators = len(validators)
            
            if working_validators >= total_validators * 0.8:  # 80% threshold
                return {
                    'status': 'PASS',
                    'message': 'Automated validation systems working',
                    'details': f'{working_validators}/{total_validators} validators operational'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Automated validation systems have issues',
                    'details': f'Only {working_validators}/{total_validators} validators working'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not test automated validation',
                'details': str(e)
            }

    def _test_monitoring_stability(self) -> Dict:
        """Test continuous monitoring shows healthy status"""
        try:
            # Check monitoring log for recent healthy status
            monitoring_files = [
                '/var/log/emergent_tunnel_watchdog.log',
                '/app/monitoring.log'
            ]
            
            healthy_indicators = 0
            error_indicators = 0
            
            for log_file in monitoring_files:
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        recent_lines = f.readlines()[-50:]  # Last 50 lines
                        for line in recent_lines:
                            if '✅' in line or 'healthy' in line.lower() or 'success' in line.lower():
                                healthy_indicators += 1
                            elif '❌' in line or 'error' in line.lower() or 'fail' in line.lower():
                                error_indicators += 1
            
            if healthy_indicators > error_indicators * 2:  # Healthy should be at least 2x errors
                return {
                    'status': 'PASS',
                    'message': 'Monitoring shows consistent healthy status',
                    'details': f'Healthy: {healthy_indicators}, Errors: {error_indicators}'
                }
            elif healthy_indicators > error_indicators:
                return {
                    'status': 'WARN',
                    'message': 'Monitoring shows mostly healthy status',
                    'details': f'Healthy: {healthy_indicators}, Errors: {error_indicators}'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Monitoring shows concerning error levels',
                    'details': f'Healthy: {healthy_indicators}, Errors: {error_indicators}'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not test monitoring stability',
                'details': str(e)
            }

    def _test_error_prevention(self) -> Dict:
        """Test that no legacy tunnel-related errors occur"""
        try:
            # Test various scenarios that previously caused ERR_NGROK_3200
            test_scenarios = [
                ('API health check', f'{self.api_base}/'),
                ('Station info', f'{self.api_base}/station-info'),
                ('Radio streams', f'{self.api_base}/radio/streams'),
                ('App version', f'{self.api_base}/app/version')
            ]
            
            error_free_requests = 0
            total_requests = len(test_scenarios)
            
            for scenario_name, url in test_scenarios:
                try:
                    response = self.session.get(url, timeout=5)
                    if response.status_code == 200:
                        error_free_requests += 1
                        self.log_test(f"Error prevention test - {scenario_name}: OK", "PASS")
                    else:
                        self.log_test(f"Error prevention test - {scenario_name}: HTTP {response.status_code}", "FAIL")
                except Exception as e:
                    self.log_test(f"Error prevention test - {scenario_name}: {str(e)}", "FAIL")
            
            success_rate = (error_free_requests / total_requests) * 100
            
            if success_rate == 100:
                return {
                    'status': 'PASS',
                    'message': 'No legacy tunnel-related errors detected',
                    'details': f'All {total_requests} error prevention tests passed'
                }
            elif success_rate >= 80:
                return {
                    'status': 'WARN',
                    'message': 'Minimal errors detected in prevention tests',
                    'details': f'{success_rate:.1f}% success rate'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Multiple errors detected in prevention tests',
                    'details': f'{success_rate:.1f}% success rate'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not test error prevention',
                'details': str(e)
            }

    def _test_health_check_systems(self) -> Dict:
        """Test health check systems are working"""
        try:
            # Test the health check script
            health_script = '/app/check_tunnel_health.py'
            if os.path.exists(health_script):
                result = subprocess.run(['python3', health_script], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    return {
                        'status': 'PASS',
                        'message': 'Health check systems operational',
                        'details': 'Health check script executed successfully'
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'message': 'Health check systems have issues',
                        'details': f'Health check script failed: {result.stderr[:200]}'
                    }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Health check script missing',
                    'details': f'Script not found at {health_script}'
                }
        except subprocess.TimeoutExpired:
            return {
                'status': 'FAIL',
                'message': 'Health check script timeout',
                'details': 'Health check took too long to complete'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not test health check systems',
                'details': str(e)
            }

    def _test_api_response_times(self) -> Dict:
        """Test all endpoints respond under 500ms through Emergent tunnels"""
        try:
            endpoints = [
                '/',
                '/station-info',
                '/languages',
                '/radio/streams',
                '/radio/stations',
                '/app/info',
                '/app/version'
            ]
            
            response_times = []
            slow_endpoints = []
            
            for endpoint in endpoints:
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.api_base}{endpoint}", timeout=10)
                    response_time = time.time() - start_time
                    response_times.append(response_time)
                    
                    if response_time > 0.5:  # 500ms threshold
                        slow_endpoints.append(f"{endpoint}: {response_time:.3f}s")
                        
                except Exception as e:
                    slow_endpoints.append(f"{endpoint}: Error - {str(e)}")
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            if not slow_endpoints and avg_response_time < 0.5:
                return {
                    'status': 'PASS',
                    'message': 'All API endpoints respond under 500ms',
                    'details': f'Average response time: {avg_response_time:.3f}s'
                }
            elif len(slow_endpoints) <= 1:  # Allow 1 slow endpoint
                return {
                    'status': 'WARN',
                    'message': 'Most API endpoints meet performance target',
                    'details': f'Slow endpoints: {slow_endpoints}'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Multiple API endpoints exceed 500ms target',
                    'details': f'Slow endpoints: {slow_endpoints}'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not test API response times',
                'details': str(e)
            }

    def _test_concurrent_request_handling(self) -> Dict:
        """Test system handles multiple simultaneous requests"""
        try:
            def make_request(endpoint):
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.api_base}{endpoint}", timeout=10)
                    response_time = time.time() - start_time
                    return {
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'success': response.status_code == 200
                    }
                except Exception as e:
                    return {
                        'endpoint': endpoint,
                        'status_code': 0,
                        'response_time': 0,
                        'success': False,
                        'error': str(e)
                    }
            
            # Test with 10 concurrent requests to different endpoints
            endpoints = ['/', '/station-info', '/languages', '/radio/streams', '/radio/stations'] * 2
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                start_time = time.time()
                futures = [executor.submit(make_request, endpoint) for endpoint in endpoints]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
                total_time = time.time() - start_time
            
            successful_requests = sum(1 for r in results if r['success'])
            total_requests = len(results)
            success_rate = (successful_requests / total_requests) * 100
            avg_response_time = sum(r['response_time'] for r in results if r['success']) / successful_requests if successful_requests > 0 else 0
            
            if success_rate >= 95 and total_time < 5:  # 95% success in under 5 seconds
                return {
                    'status': 'PASS',
                    'message': 'System handles concurrent requests well',
                    'details': f'Success rate: {success_rate:.1f}%, Total time: {total_time:.3f}s, Avg response: {avg_response_time:.3f}s'
                }
            elif success_rate >= 80:
                return {
                    'status': 'WARN',
                    'message': 'System handles most concurrent requests',
                    'details': f'Success rate: {success_rate:.1f}%, Total time: {total_time:.3f}s'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'System struggles with concurrent requests',
                    'details': f'Success rate: {success_rate:.1f}%, Total time: {total_time:.3f}s'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not test concurrent request handling',
                'details': str(e)
            }

    def _test_tunnel_reliability(self) -> Dict:
        """Test consistent connectivity over extended period"""
        try:
            # Test connectivity over 2 minutes with requests every 10 seconds
            test_duration = 120  # 2 minutes
            interval = 10  # 10 seconds
            test_count = test_duration // interval
            
            self.log_test(f"Testing tunnel reliability over {test_duration} seconds...", "INFO")
            
            successful_tests = 0
            response_times = []
            
            for i in range(test_count):
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.api_base}/", timeout=5)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        successful_tests += 1
                        response_times.append(response_time)
                        self.log_test(f"Reliability test {i+1}/{test_count}: OK ({response_time:.3f}s)", "PASS")
                    else:
                        self.log_test(f"Reliability test {i+1}/{test_count}: HTTP {response.status_code}", "FAIL")
                        
                except Exception as e:
                    self.log_test(f"Reliability test {i+1}/{test_count}: Error - {str(e)}", "FAIL")
                
                if i < test_count - 1:  # Don't sleep after last test
                    time.sleep(interval)
            
            reliability_rate = (successful_tests / test_count) * 100
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            if reliability_rate >= 95:
                return {
                    'status': 'PASS',
                    'message': 'Tunnel shows excellent reliability',
                    'details': f'Reliability: {reliability_rate:.1f}%, Avg response: {avg_response_time:.3f}s'
                }
            elif reliability_rate >= 80:
                return {
                    'status': 'WARN',
                    'message': 'Tunnel shows good reliability',
                    'details': f'Reliability: {reliability_rate:.1f}%, Avg response: {avg_response_time:.3f}s'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Tunnel reliability below acceptable threshold',
                    'details': f'Reliability: {reliability_rate:.1f}%, Avg response: {avg_response_time:.3f}s'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not test tunnel reliability',
                'details': str(e)
            }

    def _test_sustained_load_performance(self) -> Dict:
        """Test performance under sustained load"""
        try:
            # Simulate sustained load for 1 minute
            load_duration = 60  # 1 minute
            requests_per_second = 2
            total_requests = load_duration * requests_per_second
            
            self.log_test(f"Testing sustained load performance ({total_requests} requests over {load_duration}s)...", "INFO")
            
            def make_load_request():
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.api_base}/station-info", timeout=5)
                    response_time = time.time() - start_time
                    return {
                        'success': response.status_code == 200,
                        'response_time': response_time,
                        'status_code': response.status_code
                    }
                except Exception:
                    return {
                        'success': False,
                        'response_time': 0,
                        'status_code': 0
                    }
            
            results = []
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                for i in range(total_requests):
                    future = executor.submit(make_load_request)
                    results.append(future)
                    
                    # Control request rate
                    elapsed = time.time() - start_time
                    expected_time = i / requests_per_second
                    if elapsed < expected_time:
                        time.sleep(expected_time - elapsed)
                
                # Collect results
                completed_results = [future.result() for future in results]
            
            successful_requests = sum(1 for r in completed_results if r['success'])
            success_rate = (successful_requests / total_requests) * 100
            avg_response_time = sum(r['response_time'] for r in completed_results if r['success']) / successful_requests if successful_requests > 0 else 0
            
            if success_rate >= 95 and avg_response_time < 1.0:
                return {
                    'status': 'PASS',
                    'message': 'System performs well under sustained load',
                    'details': f'Success rate: {success_rate:.1f}%, Avg response: {avg_response_time:.3f}s'
                }
            elif success_rate >= 80:
                return {
                    'status': 'WARN',
                    'message': 'System handles sustained load with some degradation',
                    'details': f'Success rate: {success_rate:.1f}%, Avg response: {avg_response_time:.3f}s'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'System struggles under sustained load',
                    'details': f'Success rate: {success_rate:.1f}%, Avg response: {avg_response_time:.3f}s'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not test sustained load performance',
                'details': str(e)
            }

    def _test_all_services_running(self) -> Dict:
        """Test that backend, frontend, and tunnel monitoring are all operational"""
        try:
            required_services = [
                'backend',
                'frontend', 
                'emergent-tunnel-watchdog'
            ]
            
            service_status = {}
            for service in required_services:
                result = subprocess.run(['supervisorctl', 'status', service], 
                                      capture_output=True, text=True)
                service_status[service] = {
                    'running': 'RUNNING' in result.stdout,
                    'status': result.stdout.strip()
                }
            
            running_services = [k for k, v in service_status.items() if v['running']]
            
            if len(running_services) == len(required_services):
                return {
                    'status': 'PASS',
                    'message': 'All required services operational',
                    'details': f'Running services: {", ".join(running_services)}'
                }
            else:
                failed_services = [k for k, v in service_status.items() if not v['running']]
                return {
                    'status': 'FAIL',
                    'message': 'Some required services not running',
                    'details': f'Failed services: {failed_services}'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not check service status',
                'details': str(e)
            }

    def _test_no_error_conditions(self) -> Dict:
        """Test no tunnel-related errors or warnings in logs"""
        try:
            error_patterns = [
                'err_ngrok_3200',
                'ngrok.*error',
                'tunnel.*error',
                'connection.*failed',
                'timeout.*tunnel'
            ]
            
            log_files = [
                '/var/log/supervisor/backend.err.log',
                '/var/log/supervisor/frontend.err.log',
                '/var/log/emergent_tunnel_watchdog.log'
            ]
            
            errors_found = []
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r') as f:
                            content = f.read().lower()
                            for pattern in error_patterns:
                                if pattern in content:
                                    errors_found.append(f'{log_file}: {pattern}')
                    except Exception:
                        continue
            
            if not errors_found:
                return {
                    'status': 'PASS',
                    'message': 'No tunnel-related errors or warnings found',
                    'details': f'Checked {len(log_files)} log files for {len(error_patterns)} error patterns'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Tunnel-related errors found in logs',
                    'details': f'Errors: {"; ".join(errors_found[:3])}'  # Show first 3
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not check for error conditions',
                'details': str(e)
            }

    def _test_documentation_complete(self) -> Dict:
        """Test that all preventive measures are documented and accessible"""
        try:
            required_docs = [
                '/app/TUNNEL_SYSTEM_DOCS.md',
                '/app/TUNNEL_MANAGEMENT_README.md',
                '/app/ERR_NGROK_3200_INVESTIGATION_REPORT.md',
                '/app/PREVENTIVE_ACTIONS_SUMMARY.md'
            ]
            
            doc_status = {}
            for doc in required_docs:
                if os.path.exists(doc):
                    with open(doc, 'r') as f:
                        content = f.read()
                        doc_status[doc] = {
                            'exists': True,
                            'size': len(content),
                            'has_emergent_info': 'emergent' in content.lower(),
                            'has_prevention_info': 'prevent' in content.lower()
                        }
                else:
                    doc_status[doc] = {
                        'exists': False,
                        'size': 0,
                        'has_emergent_info': False,
                        'has_prevention_info': False
                    }
            
            existing_docs = sum(1 for status in doc_status.values() if status['exists'])
            complete_docs = sum(1 for status in doc_status.values() 
                              if status['exists'] and status['size'] > 100)
            
            if complete_docs >= len(required_docs) * 0.8:  # 80% threshold
                return {
                    'status': 'PASS',
                    'message': 'Documentation complete and accessible',
                    'details': f'{complete_docs}/{len(required_docs)} documentation files complete'
                }
            elif existing_docs >= len(required_docs) * 0.6:  # 60% threshold
                return {
                    'status': 'WARN',
                    'message': 'Most documentation present but some incomplete',
                    'details': f'{existing_docs}/{len(required_docs)} files exist, {complete_docs} complete'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Documentation incomplete or missing',
                    'details': f'Only {existing_docs}/{len(required_docs)} files exist'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not check documentation completeness',
                'details': str(e)
            }

    def _test_monitoring_systems_active(self) -> Dict:
        """Test monitoring systems are active and reporting"""
        try:
            monitoring_components = {
                'emergent_tunnel_watchdog': '/var/log/emergent_tunnel_watchdog.log',
                'automated_monitoring': '/app/monitoring.log',
                'health_checker': '/app/check_tunnel_health.py'
            }
            
            active_components = 0
            component_details = []
            
            for component, path in monitoring_components.items():
                if component == 'health_checker':
                    # Check if script exists and is executable
                    if os.path.exists(path) and os.access(path, os.X_OK):
                        active_components += 1
                        component_details.append(f'{component}: executable')
                    else:
                        component_details.append(f'{component}: missing or not executable')
                else:
                    # Check if log file exists and has recent entries
                    if os.path.exists(path):
                        try:
                            stat = os.stat(path)
                            age_hours = (time.time() - stat.st_mtime) / 3600
                            if age_hours < 24:  # Updated within 24 hours
                                active_components += 1
                                component_details.append(f'{component}: active (updated {age_hours:.1f}h ago)')
                            else:
                                component_details.append(f'{component}: stale (updated {age_hours:.1f}h ago)')
                        except Exception:
                            component_details.append(f'{component}: error checking file')
                    else:
                        component_details.append(f'{component}: log file missing')
            
            total_components = len(monitoring_components)
            
            if active_components == total_components:
                return {
                    'status': 'PASS',
                    'message': 'All monitoring systems active and reporting',
                    'details': '; '.join(component_details)
                }
            elif active_components >= total_components * 0.7:  # 70% threshold
                return {
                    'status': 'WARN',
                    'message': 'Most monitoring systems active',
                    'details': '; '.join(component_details)
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Multiple monitoring systems inactive',
                    'details': '; '.join(component_details)
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not check monitoring systems',
                'details': str(e)
            }

    def run_comprehensive_validation(self):
        """Run all validation categories"""
        self.log_test("🚀 Starting ERR_NGROK_3200 Comprehensive Resolution Validation", "INFO")
        self.log_test("=" * 80, "INFO")
        
        # Run all validation categories
        validation_methods = [
            self.validate_ngrok_error_resolution,
            self.validate_corrective_actions,
            self.validate_preventive_actions,
            self.validate_system_performance_under_load,
            self.validate_production_readiness
        ]
        
        for method in validation_methods:
            try:
                result = method()
                category_name = result['category']
                passed = result['passed_tests']
                total = result['total_tests']
                success_rate = (passed / total) * 100 if total > 0 else 0
                
                if success_rate >= 95:
                    self.log_test(f"✅ EXCELLENT [{category_name}] - {success_rate:.1f}% ({passed}/{total})", "PASS")
                elif success_rate >= 80:
                    self.log_test(f"⚠️ GOOD [{category_name}] - {success_rate:.1f}% ({passed}/{total})", "WARN")
                else:
                    self.log_test(f"❌ NEEDS ATTENTION [{category_name}] - {success_rate:.1f}% ({passed}/{total})", "FAIL")
                    
            except Exception as e:
                self.log_test(f"❌ ERROR in {method.__name__}: {str(e)}", "FAIL")
        
        # Calculate overall results
        total_tests = sum(cat['total_tests'] for cat in self.test_results['validation_categories'].values())
        passed_tests = sum(cat['passed_tests'] for cat in self.test_results['validation_categories'].values())
        failed_tests = total_tests - passed_tests
        overall_success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        self.test_results['validation_summary'].update({
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_resolution_status': self._determine_resolution_status(overall_success_rate),
            'production_ready': overall_success_rate >= 95
        })
        
        # Print final summary
        self.log_test("=" * 80, "INFO")
        self.log_test("📊 ERR_NGROK_3200 COMPREHENSIVE VALIDATION SUMMARY", "INFO")
        self.log_test("=" * 80, "INFO")
        
        status = self.test_results['validation_summary']['error_resolution_status']
        if status == 'COMPLETELY_RESOLVED':
            self.log_test(f"🎉 EXCELLENT: ERR_NGROK_3200 issue completely resolved ({overall_success_rate:.1f}%)", "PASS")
        elif status == 'MOSTLY_RESOLVED':
            self.log_test(f"✅ GOOD: ERR_NGROK_3200 issue mostly resolved ({overall_success_rate:.1f}%)", "WARN")
        else:
            self.log_test(f"❌ CRITICAL: ERR_NGROK_3200 issue not fully resolved ({overall_success_rate:.1f}%)", "FAIL")
        
        self.log_test(f"Total Tests: {total_tests}", "INFO")
        self.log_test(f"Passed: {passed_tests}", "INFO")
        self.log_test(f"Failed: {failed_tests}", "INFO")
        self.log_test(f"Production Ready: {'YES' if self.test_results['validation_summary']['production_ready'] else 'NO'}", "INFO")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"/app/err_ngrok_3200_comprehensive_validation_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        self.log_test(f"📄 Results saved to: {results_file}", "INFO")
        return self.test_results

    def _determine_resolution_status(self, success_rate: float) -> str:
        """Determine overall resolution status based on success rate"""
        if success_rate >= 95:
            return 'COMPLETELY_RESOLVED'
        elif success_rate >= 80:
            return 'MOSTLY_RESOLVED'
        else:
            return 'PARTIALLY_RESOLVED'

def main():
    """Main execution function"""
    validator = ERRNgrok3200ComprehensiveValidator()
    results = validator.run_comprehensive_validation()
    
    # Exit with appropriate code
    if results['validation_summary']['production_ready']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Issues found

if __name__ == "__main__":
    main()