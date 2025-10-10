#!/usr/bin/env python3
"""
ERR_NGROK_3200 Resolution Testing Suite
Comprehensive testing to verify the complete resolution of the ERR_NGROK_3200 issue
"""

import requests
import subprocess
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple

class ERRNgrok3200ResolutionTester:
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'test_summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'error_resolution_status': 'UNKNOWN'
            },
            'test_categories': {}
        }
        
    def test_legacy_ngrok_removal(self) -> Dict:
        """Test that all legacy ngrok references have been removed"""
        print("🔍 Testing legacy ngrok reference removal...")
        
        tests = {
            'ngrok_process_check': self._test_no_ngrok_processes(),
            'ngrok_api_unavailable': self._test_ngrok_api_unavailable(),  
            'legacy_watchdog_stopped': self._test_legacy_watchdog_stopped(),
            'legacy_files_archived': self._test_legacy_files_archived()
        }
        
        category_result = {
            'category': 'Legacy NGROK Removal',
            'total_tests': len(tests),
            'passed_tests': sum(1 for result in tests.values() if result['status'] == 'PASS'),
            'tests': tests
        }
        
        self.test_results['test_categories']['legacy_ngrok_removal'] = category_result
        return category_result
    
    def _test_no_ngrok_processes(self) -> Dict:
        """Test that no ngrok processes are running"""
        try:
            # Look specifically for ngrok binary, not just anything containing "ngrok"
            result = subprocess.run(['pgrep', '-f', '^ngrok'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:  # No processes found
                # Double check by looking for actual ngrok binary
                ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                if ' ngrok ' not in ps_result.stdout and '/ngrok' not in ps_result.stdout:
                    return {
                        'status': 'PASS',
                        'message': 'No ngrok processes running',
                        'details': 'No ngrok binary processes detected'
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'message': 'Legacy ngrok processes detected in ps output',
                        'details': 'Found ngrok references in process list'
                    }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Legacy ngrok processes still running',
                    'details': f'Found processes: {result.stdout.strip()}'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not check for ngrok processes',
                'details': str(e)
            }
    
    def _test_ngrok_api_unavailable(self) -> Dict:
        """Test that ngrok API is not accessible (as expected)"""
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            return {
                'status': 'FAIL',
                'message': 'Ngrok API unexpectedly accessible',
                'details': f'HTTP {response.status_code}'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'PASS', 
                'message': 'Ngrok API correctly unavailable',
                'details': 'Connection refused as expected'
            }
        except Exception as e:
            return {
                'status': 'PASS',
                'message': 'Ngrok API correctly unavailable',
                'details': f'Expected error: {str(e)}'
            }
    
    def _test_legacy_watchdog_stopped(self) -> Dict:
        """Test that legacy tunnel watchdog is stopped"""
        try:
            result = subprocess.run(['supervisorctl', 'status', 'tunnel-watchdog'], 
                                  capture_output=True, text=True)
            
            if 'no such process' in result.stderr.lower() or result.returncode != 0:
                return {
                    'status': 'PASS',
                    'message': 'Legacy tunnel-watchdog correctly removed',
                    'details': 'Process not found in supervisor'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Legacy tunnel-watchdog still exists',
                    'details': result.stdout.strip()
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not check watchdog status',
                'details': str(e)
            }
    
    def _test_legacy_files_archived(self) -> Dict:
        """Test that legacy files have been properly archived"""
        import os
        
        legacy_files = [
            '/app/tunnel_watchdog.sh',
            '/app/tunnel_manager.py'
        ]
        
        archived_count = 0
        details = []
        
        for file_path in legacy_files:
            if not os.path.exists(file_path):
                archived_count += 1
                details.append(f"{file_path} - Correctly removed/archived")
                
                # Check if archived version exists
                archived_pattern = f"{file_path}.legacy_archived_"
                for filename in os.listdir('/app'):
                    if filename.startswith(os.path.basename(file_path) + '.legacy_archived_'):
                        details.append(f"  -> Archived as: {filename}")
                        break
            else:
                details.append(f"{file_path} - Still exists (should be archived)")
        
        if archived_count == len(legacy_files):
            return {
                'status': 'PASS',
                'message': 'All legacy files properly archived',
                'details': '; '.join(details)
            }
        else:
            return {
                'status': 'PARTIAL',
                'message': f'{archived_count}/{len(legacy_files)} legacy files archived',
                'details': '; '.join(details)
            }
    
    def test_emergent_tunnel_functionality(self) -> Dict:
        """Test that Emergent tunnel system is working correctly"""
        print("🌐 Testing Emergent tunnel functionality...")
        
        base_url = "https://carmedia-hub-1.preview.emergentagent.com"
        
        tests = {
            'backend_connectivity': self._test_backend_connectivity(base_url),
            'frontend_connectivity': self._test_frontend_connectivity(base_url),
            'new_watchdog_running': self._test_new_watchdog_running(),
            'performance_acceptable': self._test_performance_acceptable(base_url)
        }
        
        category_result = {
            'category': 'Emergent Tunnel Functionality',
            'total_tests': len(tests),
            'passed_tests': sum(1 for result in tests.values() if result['status'] == 'PASS'),
            'tests': tests
        }
        
        self.test_results['test_categories']['emergent_tunnel_functionality'] = category_result
        return category_result
    
    def _test_backend_connectivity(self, base_url: str) -> Dict:
        """Test backend API connectivity"""
        try:
            response = requests.get(f"{base_url}/api/", timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'PASS',
                    'message': 'Backend API accessible and healthy',
                    'details': f'HTTP {response.status_code}, {response.elapsed.total_seconds():.3f}s'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Backend API returned error status',
                    'details': f'HTTP {response.status_code}'
                }
        except Exception as e:
            return {
                'status': 'FAIL',
                'message': 'Backend API connectivity failed',
                'details': str(e)
            }
    
    def _test_frontend_connectivity(self, base_url: str) -> Dict:
        """Test frontend connectivity"""
        try:
            response = requests.get(f"{base_url}/", timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'PASS',
                    'message': 'Frontend accessible and healthy',
                    'details': f'HTTP {response.status_code}, {response.elapsed.total_seconds():.3f}s'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Frontend returned error status',
                    'details': f'HTTP {response.status_code}'
                }
        except Exception as e:
            return {
                'status': 'FAIL',
                'message': 'Frontend connectivity failed',
                'details': str(e)
            }
    
    def _test_new_watchdog_running(self) -> Dict:
        """Test that new Emergent watchdog is running"""
        try:
            result = subprocess.run(['supervisorctl', 'status', 'emergent-tunnel-watchdog'], 
                                  capture_output=True, text=True)
            
            if 'RUNNING' in result.stdout:
                return {
                    'status': 'PASS',
                    'message': 'Emergent tunnel watchdog running correctly',
                    'details': result.stdout.strip()
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
                'message': 'Could not check new watchdog status',
                'details': str(e)
            }
    
    def _test_performance_acceptable(self, base_url: str) -> Dict:
        """Test that tunnel performance is acceptable"""
        try:
            # Test multiple requests to get average
            response_times = []
            
            for _ in range(3):
                response = requests.get(f"{base_url}/api/", timeout=10)
                if response.status_code == 200:
                    response_times.append(response.elapsed.total_seconds())
                else:
                    return {
                        'status': 'FAIL',
                        'message': 'Performance test failed due to errors',
                        'details': f'HTTP {response.status_code}'
                    }
            
            avg_time = sum(response_times) / len(response_times)
            
            if avg_time < 2.0:  # Less than 2 seconds is acceptable
                return {
                    'status': 'PASS',
                    'message': 'Tunnel performance acceptable',
                    'details': f'Average response time: {avg_time:.3f}s'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Tunnel performance degraded',
                    'details': f'Average response time: {avg_time:.3f}s (>2s threshold)'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Performance test failed',
                'details': str(e)
            }
    
    def test_error_prevention_measures(self) -> Dict:
        """Test that preventive measures are in place"""
        print("🛡️ Testing error prevention measures...")
        
        tests = {
            'config_validator_exists': self._test_config_validator_exists(),
            'health_checker_exists': self._test_health_checker_exists(),
            'documentation_updated': self._test_documentation_updated(),
            'monitoring_logs_healthy': self._test_monitoring_logs_healthy()
        }
        
        category_result = {
            'category': 'Error Prevention Measures',
            'total_tests': len(tests),
            'passed_tests': sum(1 for result in tests.values() if result['status'] == 'PASS'),
            'tests': tests
        }
        
        self.test_results['test_categories']['error_prevention_measures'] = category_result
        return category_result
    
    def _test_config_validator_exists(self) -> Dict:
        """Test that configuration validator exists and works"""
        import os
        
        validator_path = '/app/validate_tunnel_config.py'
        
        if not os.path.exists(validator_path):
            return {
                'status': 'FAIL',
                'message': 'Configuration validator not found',
                'details': f'Missing: {validator_path}'
            }
        
        try:
            result = subprocess.run([validator_path], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'status': 'PASS',
                    'message': 'Configuration validator working correctly',
                    'details': result.stdout.strip()
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Configuration validator found issues',
                    'details': result.stdout.strip()
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not run configuration validator',
                'details': str(e)
            }
    
    def _test_health_checker_exists(self) -> Dict:
        """Test that health checker exists and works"""
        import os
        
        health_checker_path = '/app/check_tunnel_health.py'
        
        if not os.path.exists(health_checker_path):
            return {
                'status': 'FAIL',
                'message': 'Health checker not found',
                'details': f'Missing: {health_checker_path}'
            }
        
        try:
            result = subprocess.run([health_checker_path], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'status': 'PASS',
                    'message': 'Health checker working correctly',
                    'details': 'System health validated successfully'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Health checker found issues',
                    'details': result.stdout.strip()
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not run health checker',
                'details': str(e)
            }
    
    def _test_documentation_updated(self) -> Dict:
        """Test that documentation has been updated"""
        import os
        
        docs_path = '/app/TUNNEL_SYSTEM_DOCS.md'
        
        if not os.path.exists(docs_path):
            return {
                'status': 'FAIL',
                'message': 'Tunnel system documentation not found',
                'details': f'Missing: {docs_path}'
            }
        
        try:
            with open(docs_path, 'r') as f:
                content = f.read()
                
            if 'Emergent Platform Tunnels' in content and 'DEPRECATED' in content:
                return {
                    'status': 'PASS',
                    'message': 'Documentation properly updated',
                    'details': 'Contains Emergent tunnel info and legacy deprecation notices'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Documentation not properly updated',
                    'details': 'Missing expected content sections'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not read documentation',
                'details': str(e)
            }
    
    def _test_monitoring_logs_healthy(self) -> Dict:
        """Test that monitoring logs show healthy status"""
        import os
        
        log_path = '/var/log/emergent_tunnel_watchdog.log'
        
        if not os.path.exists(log_path):
            return {
                'status': 'FAIL',
                'message': 'Monitoring log file not found',
                'details': f'Missing: {log_path}'
            }
        
        try:
            with open(log_path, 'r') as f:
                lines = f.readlines()
            
            recent_lines = lines[-10:]  # Check last 10 lines
            healthy_count = sum(1 for line in recent_lines if '✅' in line and 'healthy' in line.lower())
            error_count = sum(1 for line in recent_lines if '❌' in line or 'ERROR' in line)
            
            if healthy_count > 0 and error_count == 0:
                return {
                    'status': 'PASS',
                    'message': 'Monitoring logs show healthy status',
                    'details': f'Found {healthy_count} healthy status messages, no errors'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': 'Monitoring logs show issues',
                    'details': f'Healthy: {healthy_count}, Errors: {error_count}'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': 'Could not read monitoring logs',
                'details': str(e)
            }
    
    def determine_overall_resolution_status(self) -> str:
        """Determine if ERR_NGROK_3200 has been fully resolved"""
        total_tests = 0
        passed_tests = 0
        
        for category in self.test_results['test_categories'].values():
            total_tests += category['total_tests']
            passed_tests += category['passed_tests']
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        if success_rate >= 95:
            return 'FULLY_RESOLVED'
        elif success_rate >= 80:
            return 'MOSTLY_RESOLVED'
        elif success_rate >= 60:
            return 'PARTIALLY_RESOLVED'
        else:
            return 'NOT_RESOLVED'
    
    def run_comprehensive_resolution_test(self) -> Dict:
        """Run comprehensive test suite to verify ERR_NGROK_3200 resolution"""
        print("🚀 Starting ERR_NGROK_3200 Resolution Testing Suite")
        print("=" * 80)
        
        # Run all test categories
        self.test_legacy_ngrok_removal()
        self.test_emergent_tunnel_functionality()
        self.test_error_prevention_measures()
        
        # Calculate overall results
        total_tests = 0
        passed_tests = 0
        
        for category in self.test_results['test_categories'].values():
            total_tests += category['total_tests']
            passed_tests += category['passed_tests']
        
        self.test_results['test_summary']['total_tests'] = total_tests
        self.test_results['test_summary']['passed_tests'] = passed_tests
        self.test_results['test_summary']['failed_tests'] = total_tests - passed_tests
        self.test_results['test_summary']['error_resolution_status'] = self.determine_overall_resolution_status()
        
        return self.test_results
    
    def print_test_results(self) -> None:
        """Print detailed test results"""
        print("\n" + "=" * 80)
        print("📊 ERR_NGROK_3200 RESOLUTION TEST RESULTS")
        print("=" * 80)
        
        summary = self.test_results['test_summary']
        success_rate = (summary['passed_tests'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        
        print(f"\n🎯 Overall Resolution Status: {summary['error_resolution_status']}")
        print(f"📈 Test Success Rate: {success_rate:.1f}% ({summary['passed_tests']}/{summary['total_tests']})")
        print(f"✅ Passed Tests: {summary['passed_tests']}")
        print(f"❌ Failed Tests: {summary['failed_tests']}")
        
        # Print category results
        for category_name, category in self.test_results['test_categories'].items():
            print(f"\n📋 {category['category']}:")
            category_success = (category['passed_tests'] / category['total_tests'] * 100)
            print(f"   Success Rate: {category_success:.1f}% ({category['passed_tests']}/{category['total_tests']})")
            
            for test_name, result in category['tests'].items():
                status_emoji = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
                print(f"   {status_emoji} {test_name}: {result['message']}")
        
        # Final assessment
        print(f"\n🎉 FINAL ASSESSMENT:")
        if summary['error_resolution_status'] == 'FULLY_RESOLVED':
            print("   ✅ ERR_NGROK_3200 has been COMPLETELY RESOLVED")
            print("   🎯 All corrective and preventive actions are effective")
            print("   🚀 System ready for production use")
        elif summary['error_resolution_status'] == 'MOSTLY_RESOLVED':
            print("   ✅ ERR_NGROK_3200 has been MOSTLY RESOLVED")
            print("   ⚠️ Minor issues remain, review failed tests")
        else:
            print("   ❌ ERR_NGROK_3200 resolution incomplete")
            print("   🔧 Additional corrective actions needed")

if __name__ == "__main__":
    tester = ERRNgrok3200ResolutionTester()
    results = tester.run_comprehensive_resolution_test()
    tester.print_test_results()
    
    # Save detailed results
    results_file = f'/app/err_ngrok_3200_resolution_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    print("=" * 80)