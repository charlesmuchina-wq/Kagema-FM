#!/usr/bin/env python3
"""
Cross-Browser Extension Conflict Testing Script
Simulates different browser contexts and extension scenarios to validate 
the Kagema FM backend's browser extension conflict prevention mechanisms.
"""

import requests
import json
import time
from typing import Dict, List, Tuple

class CrossBrowserExtensionTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.results = []
        
    def test_scenario(self, name: str, headers: Dict[str, str], expected_status: int = 200) -> Tuple[bool, Dict]:
        """Test a specific browser/extension scenario"""
        try:
            response = requests.get(
                f"{self.base_url}/api/",
                headers=headers,
                timeout=10
            )
            
            success = response.status_code == expected_status
            result = {
                "name": name,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success,
                "headers": dict(response.headers),
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "has_security_headers": self._check_security_headers(response.headers)
            }
            
            if response.status_code == 200:
                try:
                    result["response_data"] = response.json()
                except:
                    result["response_data"] = response.text[:100]
            
            self.results.append(result)
            return success, result
            
        except requests.exceptions.RequestException as e:
            result = {
                "name": name,
                "expected_status": expected_status,
                "actual_status": "ERROR",
                "success": False,
                "error": str(e),
                "response_time_ms": 0,
                "has_security_headers": False
            }
            self.results.append(result)
            return False, result
    
    def _check_security_headers(self, headers: Dict[str, str]) -> bool:
        """Check if response includes required security headers"""
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Referrer-Policy"
        ]
        return all(header.lower() in [h.lower() for h in headers.keys()] for header in required_headers)
    
    def run_comprehensive_tests(self):
        """Run comprehensive cross-browser extension conflict tests"""
        print("🔒 Starting Comprehensive Cross-Browser Extension Conflict Testing...")
        print("=" * 80)
        
        # Test 1: Browser Extension Origins (Should be blocked - 403)
        print("\n📱 Testing Browser Extension Origins (Should be blocked - 403)")
        extension_scenarios = [
            ("Chrome Extension", {"origin": "chrome-extension://abcdefghijklmnop", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}),
            ("Firefox Extension", {"origin": "moz-extension://12345678-1234-1234-1234-123456789abc", "user-agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"}),
            ("Safari Extension", {"origin": "safari-extension://com.example.extension", "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"}),
            ("Edge Extension", {"origin": "ms-browser-extension://extension-id", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"}),
        ]
        
        for name, headers in extension_scenarios:
            success, result = self.test_scenario(name, headers, expected_status=403)
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {name}: {result['actual_status']} (Security Headers: {'Yes' if result.get('has_security_headers') else 'No'})")
        
        # Test 2: Suspicious User Agents (Should be blocked - 403)
        print("\n🕵️ Testing Suspicious User Agents (Should be blocked - 403)")
        suspicious_agents = [
            ("Extension User Agent", {"origin": "https://carmedia-hub-1.preview.emergentagent.com", "user-agent": "Mozilla/5.0 Chrome extension injector"}),
            ("Addon User Agent", {"origin": "http://localhost:3000", "user-agent": "Firefox addon enhanced browser"}),
            ("Plugin User Agent", {"origin": "https://carmedia-hub-1.preview.emergentagent.com", "user-agent": "Chrome plugin enhanced navigation"}),
            ("Mixed Case Extension", {"origin": "https://carmedia-hub-1.preview.emergentagent.com", "user-agent": "Browser Extension Manager Tool"}),
        ]
        
        for name, headers in suspicious_agents:
            success, result = self.test_scenario(name, headers, expected_status=403)
            status = "✅ PASS" if success else "❌ FAIL" 
            print(f"  {status} {name}: {result['actual_status']} (Security Headers: {'Yes' if result.get('has_security_headers') else 'No'})")
        
        # Test 3: Unauthorized Origins (Should be blocked - 403)
        print("\n🚫 Testing Unauthorized Origins (Should be blocked - 403)")
        unauthorized_origins = [
            ("Malicious Site", {"origin": "https://malicious-site.com", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}),
            ("Fake Kagema", {"origin": "https://fake-kagema.com", "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}),
            ("Phishing Domain", {"origin": "https://phishing-kagema.org", "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}),
            ("Suspicious Domain", {"origin": "http://evil-radio.net", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}),
        ]
        
        for name, headers in unauthorized_origins:
            success, result = self.test_scenario(name, headers, expected_status=403)
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {name}: {result['actual_status']} (Security Headers: {'Yes' if result.get('has_security_headers') else 'No'})")
        
        # Test 4: Legitimate Browser Contexts (Should work - 200)
        print("\n✅ Testing Legitimate Browser Contexts (Should work - 200)")
        legitimate_scenarios = [
            ("Chrome Desktop", {"origin": "https://carmedia-hub-1.preview.emergentagent.com", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}),
            ("Firefox Desktop", {"origin": "https://carmedia-hub-1.preview.emergentagent.com", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0"}),
            ("Safari Desktop", {"origin": "https://carmedia-hub-1.preview.emergentagent.com", "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"}),
            ("Chrome Mobile", {"origin": "https://carmedia-hub-1.preview.emergentagent.com", "user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"}),
            ("Safari Mobile", {"origin": "https://carmedia-hub-1.preview.emergentagent.com", "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"}),
            ("Localhost Dev", {"origin": "http://localhost:3000", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}),
        ]
        
        for name, headers in legitimate_scenarios:
            success, result = self.test_scenario(name, headers, expected_status=200)
            status = "✅ PASS" if success else "❌ FAIL"
            response_time = f"({result['response_time_ms']:.1f}ms)" if result.get('response_time_ms') else ""
            print(f"  {status} {name}: {result['actual_status']} {response_time}")
        
        # Test 5: Edge Cases and Special Scenarios
        print("\n🔧 Testing Edge Cases and Special Scenarios")
        edge_cases = [
            ("No Origin Header", {}, 200),  # Should work - direct API access
            ("Empty Origin", {"origin": "", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, 200),
            ("Mixed Case Extension Origin", {"origin": "Chrome-Extension://abcdefg", "user-agent": "Mozilla/5.0"}, 403),
            ("Extension Keyword in Origin", {"origin": "https://extension-site.com", "user-agent": "Mozilla/5.0"}, 403),
        ]
        
        for name, headers, expected in edge_cases:
            success, result = self.test_scenario(name, headers, expected_status=expected)
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {name}: {result['actual_status']}")
        
        # Performance Analysis
        self._analyze_performance()
        
        # Generate Summary Report
        self._generate_summary_report()
    
    def _analyze_performance(self):
        """Analyze performance impact of security middleware"""
        print("\n⚡ Performance Analysis")
        response_times = [r.get('response_time_ms', 0) for r in self.results if r.get('response_time_ms', 0) > 0]
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"  Average Response Time: {avg_time:.1f}ms")
            print(f"  Min Response Time: {min_time:.1f}ms")
            print(f"  Max Response Time: {max_time:.1f}ms")
            print(f"  Performance Target (<500ms): {'✅ EXCELLENT' if avg_time < 500 else '⚠️ NEEDS IMPROVEMENT'}")
    
    def _generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE CROSS-BROWSER TESTING SUMMARY REPORT")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.get('success', False))
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📈 Overall Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed Tests: {passed_tests}")
        print(f"  Failed Tests: {total_tests - passed_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        # Category breakdown
        categories = {
            "Extension Origins": [r for r in self.results if "Extension" in r['name']],
            "Suspicious User Agents": [r for r in self.results if "Agent" in r['name']],
            "Unauthorized Origins": [r for r in self.results if any(x in r['name'] for x in ["Malicious", "Fake", "Phishing", "Suspicious Domain"])],
            "Legitimate Browsers": [r for r in self.results if any(x in r['name'] for x in ["Chrome", "Firefox", "Safari", "Localhost"])],
            "Edge Cases": [r for r in self.results if any(x in r['name'] for x in ["No Origin", "Empty", "Mixed", "Keyword"])]
        }
        
        print(f"\n📋 Results by Category:")
        for category, tests in categories.items():
            if tests:
                passed = sum(1 for t in tests if t.get('success', False))
                total = len(tests)
                rate = (passed / total) * 100 if total > 0 else 0
                status = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"
                print(f"  {status} {category}: {passed}/{total} ({rate:.1f}%)")
        
        # Security Analysis
        blocked_extensions = sum(1 for r in self.results if "Extension" in r['name'] and r.get('actual_status') == 403)
        blocked_suspicious = sum(1 for r in self.results if "Agent" in r['name'] and r.get('actual_status') == 403)  
        blocked_unauthorized = sum(1 for r in self.results if any(x in r['name'] for x in ["Malicious", "Fake", "Phishing"]) and r.get('actual_status') == 403)
        
        print(f"\n🔒 Security Validation:")
        print(f"  Browser Extensions Blocked: {blocked_extensions}/4 (100.0%)" if blocked_extensions == 4 else f"  Browser Extensions Blocked: {blocked_extensions}/4 ({blocked_extensions/4*100:.1f}%)")
        print(f"  Suspicious User Agents Blocked: {blocked_suspicious}/4 (100.0%)" if blocked_suspicious == 4 else f"  Suspicious User Agents Blocked: {blocked_suspicious}/4 ({blocked_suspicious/4*100:.1f}%)")
        print(f"  Unauthorized Origins Blocked: {blocked_unauthorized}/4 (100.0%)" if blocked_unauthorized == 4 else f"  Unauthorized Origins Blocked: {blocked_unauthorized}/4 ({blocked_unauthorized/4*100:.1f}%)")
        
        # Final Assessment
        print(f"\n🎯 DEPLOYMENT READINESS ASSESSMENT:")
        if success_rate >= 95:
            print(f"  ✅ EXCELLENT - System ready for production deployment")
        elif success_rate >= 85:
            print(f"  ⚠️ GOOD - Minor issues need attention before deployment")  
        else:
            print(f"  ❌ POOR - Significant issues must be resolved before deployment")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = CrossBrowserExtensionTester()
    tester.run_comprehensive_tests()