#!/usr/bin/env python3
"""
Frontend Performance Gap Analysis
Analyzes potential frontend performance issues and optimization opportunities
"""

import requests
import json
import time
import subprocess
from typing import Dict, List, Any

class FrontendPerformanceAnalyzer:
    def __init__(self, frontend_url: str = "http://localhost:3000"):
        self.frontend_url = frontend_url
        self.results = []
        
    def analyze_bundle_size(self):
        """Analyze JavaScript bundle size and optimization opportunities"""
        print("📦 Analyzing Bundle Size and Assets...")
        
        # Check for common large assets
        test_routes = [
            "/",
            "/_expo/static/js/web/main.bundle.js",
            "/_expo/static/js/web/vendor.bundle.js",
            "/static/js/bundle.js",
        ]
        
        asset_analysis = []
        for route in test_routes:
            try:
                response = requests.head(f"{self.frontend_url}{route}", timeout=10)
                content_length = response.headers.get('content-length', '0')
                content_type = response.headers.get('content-type', 'unknown')
                
                if int(content_length) > 0:
                    asset_analysis.append({
                        'route': route,
                        'size_bytes': int(content_length),
                        'size_mb': round(int(content_length) / (1024 * 1024), 2),
                        'content_type': content_type,
                        'status': response.status_code
                    })
            except Exception as e:
                print(f"  Could not analyze {route}: {e}")
        
        # Analyze results
        total_size = sum(asset['size_bytes'] for asset in asset_analysis)
        large_assets = [asset for asset in asset_analysis if asset['size_mb'] > 2.0]
        
        print(f"  📊 Bundle Analysis Results:")
        print(f"    Total Assets Size: {round(total_size / (1024 * 1024), 2)} MB")
        print(f"    Number of Large Assets (>2MB): {len(large_assets)}")
        
        for asset in asset_analysis:
            status = "⚠️ LARGE" if asset['size_mb'] > 2.0 else "✅ OK"
            print(f"    {status} {asset['route']}: {asset['size_mb']} MB")
        
        return {
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'asset_count': len(asset_analysis),
            'large_assets': len(large_assets),
            'assets': asset_analysis
        }
    
    def analyze_load_performance(self):
        """Analyze page load performance"""
        print("\n⏱️ Analyzing Page Load Performance...")
        
        performance_tests = []
        test_urls = [
            "/",
            "/welcome", 
            "/main",
            "/enhanced"
        ]
        
        for url in test_urls:
            times = []
            for i in range(3):  # Test 3 times for average
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.frontend_url}{url}", timeout=30)
                    end_time = time.time()
                    
                    load_time = (end_time - start_time) * 1000  # Convert to ms
                    times.append(load_time)
                    
                except Exception as e:
                    print(f"    Error testing {url}: {e}")
                    times.append(30000)  # Timeout value
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            performance_tests.append({
                'url': url,
                'avg_load_time_ms': round(avg_time, 2),
                'min_load_time_ms': round(min_time, 2),
                'max_load_time_ms': round(max_time, 2),
                'consistency': 'Good' if (max_time - min_time) < 500 else 'Poor'
            })
            
            status = "✅ EXCELLENT" if avg_time < 2000 else "⚠️ SLOW" if avg_time < 5000 else "❌ VERY SLOW"
            print(f"  {status} {url}: {round(avg_time, 1)}ms (avg)")
        
        return performance_tests
    
    def analyze_network_efficiency(self):
        """Analyze network request efficiency"""
        print("\n🌐 Analyzing Network Request Efficiency...")
        
        # Test API endpoints for caching and optimization
        api_endpoints = [
            "/api/",
            "/api/station-info",
            "/api/languages",
            "/api/voice/help"
        ]
        
        network_analysis = []
        for endpoint in api_endpoints:
            try:
                # Test with and without cache headers
                start_time = time.time()
                response = requests.get(f"http://localhost:8001{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                cache_headers = {
                    'cache-control': response.headers.get('cache-control', 'None'),
                    'expires': response.headers.get('expires', 'None'),
                    'etag': response.headers.get('etag', 'None'),
                    'last-modified': response.headers.get('last-modified', 'None')
                }
                
                network_analysis.append({
                    'endpoint': endpoint,
                    'response_time_ms': round(response_time, 2),
                    'status_code': response.status_code,
                    'content_length': len(response.content),
                    'cache_headers': cache_headers,
                    'is_cacheable': 'cache-control' in response.headers or 'expires' in response.headers
                })
                
                cache_status = "✅ CACHED" if cache_headers['cache-control'] != 'None' else "⚠️ NO CACHE"
                performance_status = "✅ FAST" if response_time < 500 else "⚠️ SLOW"
                print(f"  {performance_status} {cache_status} {endpoint}: {round(response_time, 1)}ms")
                
            except Exception as e:
                print(f"  ❌ ERROR {endpoint}: {e}")
                network_analysis.append({
                    'endpoint': endpoint,
                    'error': str(e)
                })
        
        return network_analysis
    
    def analyze_memory_usage_patterns(self):
        """Analyze potential memory usage issues"""
        print("\n🧠 Analyzing Memory Usage Patterns...")
        
        # Check for potential memory leaks in component patterns
        memory_patterns = {
            'large_state_objects': 0,
            'unsubscribed_listeners': 0,
            'circular_references': 0,
            'large_arrays': 0
        }
        
        # Simulate memory analysis (in real app, this would analyze actual JS heap)
        components_to_check = [
            '/app/frontend/components/PerformanceMonitor.tsx',
            '/app/frontend/app/main.tsx',
            '/app/frontend/components/Navigation/TabNavigator.tsx'
        ]
        
        for component_path in components_to_check:
            try:
                with open(component_path, 'r') as f:
                    content = f.read()
                    
                    # Check for potential memory issues (simplified analysis)
                    if 'useState(' in content:
                        state_count = content.count('useState(')
                        if state_count > 10:
                            memory_patterns['large_state_objects'] += 1
                    
                    if 'useEffect(' in content:
                        effect_count = content.count('useEffect(')
                        cleanup_count = content.count('return () =>')
                        if effect_count > cleanup_count:
                            memory_patterns['unsubscribed_listeners'] += 1
                    
                    if 'new Array(' in content or 'Array(' in content:
                        memory_patterns['large_arrays'] += content.count('Array(')
                        
            except FileNotFoundError:
                continue
        
        # Analyze patterns
        memory_issues = sum(memory_patterns.values())
        memory_status = "✅ EXCELLENT" if memory_issues == 0 else "⚠️ NEEDS ATTENTION" if memory_issues < 5 else "❌ CRITICAL"
        
        print(f"  {memory_status} Memory Pattern Analysis:")
        print(f"    Large State Objects: {memory_patterns['large_state_objects']}")
        print(f"    Potential Unsubscribed Listeners: {memory_patterns['unsubscribed_listeners']}")
        print(f"    Large Arrays: {memory_patterns['large_arrays']}")
        
        return memory_patterns
    
    def analyze_rendering_performance(self):
        """Analyze potential rendering performance issues"""
        print("\n🎨 Analyzing Rendering Performance...")
        
        # Check for performance-impacting patterns
        rendering_issues = {
            'inline_styles': 0,
            'missing_keys': 0,
            'expensive_operations': 0,
            'unnecessary_renders': 0
        }
        
        # Analyze key components for rendering issues
        components = [
            '/app/frontend/app/main.tsx',
            '/app/frontend/components/Navigation/TabNavigator.tsx',
            '/app/frontend/components/PerformanceMonitor.tsx'
        ]
        
        for component_path in components:
            try:
                with open(component_path, 'r') as f:
                    content = f.read()
                    
                    # Check for inline styles (performance impact)
                    if 'style={{' in content:
                        rendering_issues['inline_styles'] += content.count('style={{')
                    
                    # Check for map without keys
                    if '.map(' in content and 'key=' not in content:
                        rendering_issues['missing_keys'] += content.count('.map(')
                    
                    # Check for expensive operations in render
                    expensive_ops = ['JSON.parse', 'JSON.stringify', 'sort(', 'filter(']
                    for op in expensive_ops:
                        rendering_issues['expensive_operations'] += content.count(op)
                    
                    # Check for potential unnecessary renders
                    if 'useEffect(' in content and '[]' not in content:
                        rendering_issues['unnecessary_renders'] += 1
                        
            except FileNotFoundError:
                continue
        
        total_issues = sum(rendering_issues.values())
        render_status = "✅ OPTIMIZED" if total_issues < 5 else "⚠️ NEEDS OPTIMIZATION" if total_issues < 15 else "❌ CRITICAL"
        
        print(f"  {render_status} Rendering Analysis:")
        print(f"    Inline Styles: {rendering_issues['inline_styles']}")
        print(f"    Missing Keys in Lists: {rendering_issues['missing_keys']}")
        print(f"    Expensive Operations: {rendering_issues['expensive_operations']}")
        print(f"    Potential Unnecessary Renders: {rendering_issues['unnecessary_renders']}")
        
        return rendering_issues
    
    def generate_optimization_recommendations(self, analysis_results):
        """Generate specific optimization recommendations"""
        print("\n" + "=" * 80)
        print("🎯 FRONTEND PERFORMANCE OPTIMIZATION RECOMMENDATIONS")
        print("=" * 80)
        
        recommendations = []
        
        # Bundle size recommendations
        if analysis_results.get('bundle_analysis', {}).get('large_assets', 0) > 0:
            recommendations.append({
                'category': 'Bundle Optimization',
                'priority': 'High',
                'issue': f"Large assets detected ({analysis_results['bundle_analysis']['large_assets']} assets >2MB)",
                'recommendation': 'Implement code splitting, lazy loading, and asset compression'
            })
        
        # Load performance recommendations
        slow_pages = [p for p in analysis_results.get('load_performance', []) if p['avg_load_time_ms'] > 3000]
        if slow_pages:
            recommendations.append({
                'category': 'Load Performance',
                'priority': 'High',
                'issue': f"Slow loading pages detected: {[p['url'] for p in slow_pages]}",
                'recommendation': 'Optimize initial bundle size, implement route-based code splitting'
            })
        
        # Network efficiency recommendations
        uncached_apis = [api for api in analysis_results.get('network_analysis', []) if not api.get('is_cacheable', False)]
        if uncached_apis:
            recommendations.append({
                'category': 'Network Optimization',
                'priority': 'Medium',
                'issue': f"Uncached API endpoints: {[api['endpoint'] for api in uncached_apis]}",
                'recommendation': 'Implement proper caching headers and API response caching'
            })
        
        # Memory recommendations
        memory_issues = sum(analysis_results.get('memory_patterns', {}).values())
        if memory_issues > 3:
            recommendations.append({
                'category': 'Memory Optimization',
                'priority': 'Medium',
                'issue': f"Memory usage patterns need attention ({memory_issues} potential issues)",
                'recommendation': 'Review useEffect cleanup, optimize state management, implement memory profiling'
            })
        
        # Rendering recommendations
        render_issues = sum(analysis_results.get('rendering_issues', {}).values())
        if render_issues > 10:
            recommendations.append({
                'category': 'Render Performance',
                'priority': 'Medium',
                'issue': f"Rendering optimization needed ({render_issues} potential issues)",
                'recommendation': 'Convert inline styles to StyleSheet, add React.memo, optimize re-renders'
            })
        
        # Print recommendations
        if not recommendations:
            print("🎉 EXCELLENT! No critical performance issues detected.")
            print("The frontend is well-optimized for production deployment.")
        else:
            print(f"📋 Found {len(recommendations)} optimization opportunities:")
            
            for i, rec in enumerate(recommendations, 1):
                priority_emoji = "🔴" if rec['priority'] == 'High' else "🟡" if rec['priority'] == 'Medium' else "🟢"
                print(f"\n{i}. {priority_emoji} {rec['category']} ({rec['priority']} Priority)")
                print(f"   Issue: {rec['issue']}")
                print(f"   Recommendation: {rec['recommendation']}")
        
        return recommendations
    
    def run_comprehensive_analysis(self):
        """Run complete frontend performance analysis"""
        print("🚀 Starting Comprehensive Frontend Performance Analysis...")
        print("=" * 80)
        
        analysis_results = {}
        
        # Run all analysis modules
        try:
            analysis_results['bundle_analysis'] = self.analyze_bundle_size()
        except Exception as e:
            print(f"Bundle analysis failed: {e}")
            
        try:
            analysis_results['load_performance'] = self.analyze_load_performance()
        except Exception as e:
            print(f"Load performance analysis failed: {e}")
            
        try:
            analysis_results['network_analysis'] = self.analyze_network_efficiency()
        except Exception as e:
            print(f"Network analysis failed: {e}")
            
        try:
            analysis_results['memory_patterns'] = self.analyze_memory_usage_patterns()
        except Exception as e:
            print(f"Memory analysis failed: {e}")
            
        try:
            analysis_results['rendering_issues'] = self.analyze_rendering_performance()
        except Exception as e:
            print(f"Rendering analysis failed: {e}")
        
        # Generate recommendations
        recommendations = self.generate_optimization_recommendations(analysis_results)
        
        # Calculate overall performance score
        total_issues = 0
        total_issues += analysis_results.get('bundle_analysis', {}).get('large_assets', 0) * 3  # Weight bundle issues higher
        total_issues += len([p for p in analysis_results.get('load_performance', []) if p.get('avg_load_time_ms', 0) > 3000]) * 2
        total_issues += len([api for api in analysis_results.get('network_analysis', []) if not api.get('is_cacheable', True)])
        total_issues += sum(analysis_results.get('memory_patterns', {}).values())
        total_issues += sum(analysis_results.get('rendering_issues', {}).values()) // 5  # Weight rendering issues less
        
        if total_issues == 0:
            performance_score = 100
            grade = "A+"
        elif total_issues <= 3:
            performance_score = 95
            grade = "A"
        elif total_issues <= 7:
            performance_score = 85
            grade = "B+"
        elif total_issues <= 12:
            performance_score = 75
            grade = "B"
        else:
            performance_score = max(60 - (total_issues - 12) * 5, 0)
            grade = "C" if performance_score >= 60 else "D"
        
        # Final report
        print(f"\n" + "=" * 80)
        print("📊 FRONTEND PERFORMANCE ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"\n🏆 Overall Performance Score: {performance_score}% (Grade: {grade})")
        print(f"📋 Total Issues Identified: {total_issues}")
        print(f"🎯 Optimization Recommendations: {len(recommendations)}")
        
        if performance_score >= 95:
            print("\n✅ EXCELLENT - Frontend is production-ready with optimal performance!")
        elif performance_score >= 85:
            print("\n✅ GOOD - Minor optimizations recommended for peak performance")
        elif performance_score >= 75:
            print("\n⚠️ FAIR - Several optimizations needed before production deployment")
        else:
            print("\n❌ POOR - Significant performance issues must be addressed")
        
        return {
            'performance_score': performance_score,
            'grade': grade,
            'total_issues': total_issues,
            'recommendations': recommendations,
            'detailed_analysis': analysis_results
        }

if __name__ == "__main__":
    analyzer = FrontendPerformanceAnalyzer()
    results = analyzer.run_comprehensive_analysis()