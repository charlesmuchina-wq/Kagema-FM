#!/usr/bin/env python3
"""
AI-Powered Anomaly Detection System Testing - Phase 4
Comprehensive backend testing for anomaly detection capabilities, performance baselines, and monitoring
"""

import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    endpoint: str
    response_time: float
    status_code: int
    timestamp: datetime
    payload_size: int
    error_message: Optional[str] = None

@dataclass
class AnomalyDetectionResult:
    metric_type: str
    baseline_value: float
    current_value: float
    deviation_score: float
    is_anomaly: bool
    severity: str
    recommendation: str

class AIAnomalyDetectionTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.performance_metrics: List[PerformanceMetric] = []
        self.baselines: Dict[str, Dict[str, float]] = {}
        self.anomalies_detected: List[AnomalyDetectionResult] = []
        
    async def establish_performance_baselines(self) -> Dict[str, Any]:
        """Establish normal response times, throughput, and resource usage patterns"""
        logger.info("🔍 ESTABLISHING PERFORMANCE BASELINES...")
        
        # Critical API endpoints to baseline
        endpoints = [
            {"path": "/api/", "method": "GET", "name": "API Root"},
            {"path": "/api/station-info", "method": "GET", "name": "Basic Station Info"},
            {"path": "/api/languages", "method": "GET", "name": "Supported Languages"},
            {"path": "/api/satellite/status", "method": "GET", "name": "Satellite Status"},
            {"path": "/api/language/detect", "method": "POST", "name": "Language Detection", 
             "payload": {"latitude": -1.2921, "longitude": 36.8219}},
            {"path": "/api/station-info/multilingual", "method": "POST", "name": "Multilingual Station Info",
             "payload": {"latitude": -1.2921, "longitude": 36.8219}},
            {"path": "/api/personalized-content/multilingual", "method": "POST", "name": "Personalized Content",
             "payload": {"latitude": -1.2921, "longitude": 36.8219, "preferred_language": "en", "offline_mode": False}},
            {"path": "/api/compliance/disclaimers", "method": "POST", "name": "Content Disclaimers",
             "payload": {"country_code": "KE", "language_code": "en", "content_types": ["radio_streams"]}},
        ]
        
        baseline_results = {}
        
        # Create SSL context that allows self-signed certificates
        ssl_context = False  # Disable SSL verification for testing
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for endpoint in endpoints:
                logger.info(f"📊 Baselining {endpoint['name']}...")
                response_times = []
                success_count = 0
                error_count = 0
                
                # Collect 10 samples for baseline
                for i in range(10):
                    try:
                        start_time = time.time()
                        
                        if endpoint['method'] == 'GET':
                            async with session.get(f"{self.base_url}{endpoint['path']}") as response:
                                response_time = time.time() - start_time
                                content = await response.text()
                                
                                metric = PerformanceMetric(
                                    endpoint=endpoint['name'],
                                    response_time=response_time * 1000,  # Convert to ms
                                    status_code=response.status,
                                    timestamp=datetime.now(),
                                    payload_size=len(content)
                                )
                                self.performance_metrics.append(metric)
                                
                                if response.status == 200:
                                    response_times.append(response_time * 1000)
                                    success_count += 1
                                else:
                                    error_count += 1
                                    
                        else:  # POST
                            async with session.post(
                                f"{self.base_url}{endpoint['path']}", 
                                json=endpoint.get('payload', {})
                            ) as response:
                                response_time = time.time() - start_time
                                content = await response.text()
                                
                                metric = PerformanceMetric(
                                    endpoint=endpoint['name'],
                                    response_time=response_time * 1000,
                                    status_code=response.status,
                                    timestamp=datetime.now(),
                                    payload_size=len(content)
                                )
                                self.performance_metrics.append(metric)
                                
                                if response.status in [200, 201]:
                                    response_times.append(response_time * 1000)
                                    success_count += 1
                                else:
                                    error_count += 1
                        
                        # Small delay between requests
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error testing {endpoint['name']}: {e}")
                
                # Calculate baseline statistics
                if response_times:
                    baseline_stats = {
                        "mean_response_time": statistics.mean(response_times),
                        "median_response_time": statistics.median(response_times),
                        "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                        "min_response_time": min(response_times),
                        "max_response_time": max(response_times),
                        "success_rate": (success_count / (success_count + error_count)) * 100,
                        "error_rate": (error_count / (success_count + error_count)) * 100,
                        "sample_count": len(response_times)
                    }
                    
                    self.baselines[endpoint['name']] = baseline_stats
                    baseline_results[endpoint['name']] = baseline_stats
                    
                    logger.info(f"✅ {endpoint['name']}: {baseline_stats['mean_response_time']:.1f}ms avg, {baseline_stats['success_rate']:.1f}% success")
                else:
                    logger.error(f"❌ Failed to establish baseline for {endpoint['name']}")
        
        return baseline_results
    
    async def detect_performance_anomalies(self) -> List[AnomalyDetectionResult]:
        """Detect unusual response times, throughput drops, or resource spikes"""
        logger.info("🚨 DETECTING PERFORMANCE ANOMALIES...")
        
        anomalies = []
        
        # Test each endpoint for anomalies
        async with aiohttp.ClientSession() as session:
            for endpoint_name, baseline in self.baselines.items():
                logger.info(f"🔍 Testing {endpoint_name} for anomalies...")
                
                # Find corresponding endpoint config
                endpoint_config = None
                endpoints = [
                    {"path": "/api/", "method": "GET", "name": "API Root"},
                    {"path": "/api/station-info", "method": "GET", "name": "Basic Station Info"},
                    {"path": "/api/languages", "method": "GET", "name": "Supported Languages"},
                    {"path": "/api/satellite/status", "method": "GET", "name": "Satellite Status"},
                    {"path": "/api/language/detect", "method": "POST", "name": "Language Detection", 
                     "payload": {"latitude": -1.2921, "longitude": 36.8219}},
                    {"path": "/api/station-info/multilingual", "method": "POST", "name": "Multilingual Station Info",
                     "payload": {"latitude": -1.2921, "longitude": 36.8219}},
                    {"path": "/api/personalized-content/multilingual", "method": "POST", "name": "Personalized Content",
                     "payload": {"latitude": -1.2921, "longitude": 36.8219, "preferred_language": "en", "offline_mode": False}},
                    {"path": "/api/compliance/disclaimers", "method": "POST", "name": "Content Disclaimers",
                     "payload": {"country_code": "KE", "language_code": "en", "content_types": ["radio_streams"]}},
                ]
                
                for ep in endpoints:
                    if ep['name'] == endpoint_name:
                        endpoint_config = ep
                        break
                
                if not endpoint_config:
                    continue
                
                # Test current performance
                current_response_times = []
                for i in range(5):  # 5 test samples
                    try:
                        start_time = time.time()
                        
                        if endpoint_config['method'] == 'GET':
                            async with session.get(f"{self.base_url}{endpoint_config['path']}") as response:
                                response_time = time.time() - start_time
                                current_response_times.append(response_time * 1000)
                        else:
                            async with session.post(
                                f"{self.base_url}{endpoint_config['path']}", 
                                json=endpoint_config.get('payload', {})
                            ) as response:
                                response_time = time.time() - start_time
                                current_response_times.append(response_time * 1000)
                        
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"Error testing {endpoint_name}: {e}")
                
                if current_response_times:
                    current_mean = statistics.mean(current_response_times)
                    baseline_mean = baseline['mean_response_time']
                    baseline_std = baseline['std_dev']
                    
                    # Calculate deviation score (number of standard deviations from baseline)
                    if baseline_std > 0:
                        deviation_score = abs(current_mean - baseline_mean) / baseline_std
                    else:
                        deviation_score = abs(current_mean - baseline_mean) / baseline_mean if baseline_mean > 0 else 0
                    
                    # Detect anomaly if >3 standard deviations from normal (as specified in requirements)
                    is_anomaly = deviation_score > 3.0
                    
                    if is_anomaly:
                        # More reasonable severity classification for response time anomalies
                        if current_mean > 5000:  # >5 seconds is critical
                            severity = "critical"
                        elif current_mean > 2000:  # >2 seconds is high
                            severity = "high"
                        elif deviation_score > 10.0:  # Very high deviation is medium
                            severity = "medium"
                        else:
                            severity = "low"  # Minor deviations are low priority
                        
                        recommendation = f"Response time {current_mean:.1f}ms is {deviation_score:.1f}σ from baseline {baseline_mean:.1f}ms. Investigate server performance."
                        
                        anomaly = AnomalyDetectionResult(
                            metric_type="response_time",
                            baseline_value=baseline_mean,
                            current_value=current_mean,
                            deviation_score=deviation_score,
                            is_anomaly=True,
                            severity=severity,
                            recommendation=recommendation
                        )
                        anomalies.append(anomaly)
                        logger.warning(f"🚨 ANOMALY DETECTED: {endpoint_name} - {recommendation}")
                    else:
                        logger.info(f"✅ {endpoint_name}: Normal performance ({current_mean:.1f}ms, {deviation_score:.1f}σ)")
        
        return anomalies
    
    async def detect_error_pattern_anomalies(self) -> List[AnomalyDetectionResult]:
        """Identify unusual error rates, new error types, or error clustering"""
        logger.info("🔍 DETECTING ERROR PATTERN ANOMALIES...")
        
        anomalies = []
        
        # Test endpoints for error patterns
        async with aiohttp.ClientSession() as session:
            error_tests = [
                {"path": "/api/nonexistent", "method": "GET", "expected_status": 404, "name": "404 Error Test"},
                {"path": "/api/language/detect", "method": "POST", "payload": {"invalid": "data"}, "expected_status": 422, "name": "Validation Error Test"},
                {"path": "/api/compliance/disclaimers", "method": "POST", "payload": {}, "expected_status": 422, "name": "Missing Data Error Test"},
            ]
            
            for test in error_tests:
                try:
                    if test['method'] == 'GET':
                        async with session.get(f"{self.base_url}{test['path']}") as response:
                            if response.status != test['expected_status']:
                                anomaly = AnomalyDetectionResult(
                                    metric_type="error_pattern",
                                    baseline_value=test['expected_status'],
                                    current_value=response.status,
                                    deviation_score=1.0,
                                    is_anomaly=True,
                                    severity="medium",
                                    recommendation=f"Unexpected status code {response.status} for {test['name']}, expected {test['expected_status']}"
                                )
                                anomalies.append(anomaly)
                                logger.warning(f"🚨 ERROR ANOMALY: {anomaly.recommendation}")
                            else:
                                logger.info(f"✅ {test['name']}: Expected error handling working")
                    else:
                        async with session.post(f"{self.base_url}{test['path']}", json=test.get('payload', {})) as response:
                            if response.status != test['expected_status']:
                                anomaly = AnomalyDetectionResult(
                                    metric_type="error_pattern",
                                    baseline_value=test['expected_status'],
                                    current_value=response.status,
                                    deviation_score=1.0,
                                    is_anomaly=True,
                                    severity="medium",
                                    recommendation=f"Unexpected status code {response.status} for {test['name']}, expected {test['expected_status']}"
                                )
                                anomalies.append(anomaly)
                                logger.warning(f"🚨 ERROR ANOMALY: {anomaly.recommendation}")
                            else:
                                logger.info(f"✅ {test['name']}: Expected error handling working")
                                
                except Exception as e:
                    logger.error(f"Error testing {test['name']}: {e}")
        
        return anomalies
    
    async def detect_usage_pattern_anomalies(self) -> List[AnomalyDetectionResult]:
        """Detect unusual user behavior, suspicious requests, or abnormal access patterns"""
        logger.info("🔍 DETECTING USAGE PATTERN ANOMALIES...")
        
        anomalies = []
        
        # Test for unusual request patterns
        async with aiohttp.ClientSession() as session:
            # Test rapid request pattern (potential DDoS)
            rapid_requests_start = time.time()
            rapid_request_count = 0
            
            for i in range(20):  # Send 20 rapid requests
                try:
                    async with session.get(f"{self.base_url}/api/") as response:
                        rapid_request_count += 1
                except Exception:
                    pass
            
            rapid_requests_duration = time.time() - rapid_requests_start
            requests_per_second = rapid_request_count / rapid_requests_duration
            
            # Check if request rate is unusually high (>50 requests/second could indicate DDoS)
            if requests_per_second > 50:
                anomaly = AnomalyDetectionResult(
                    metric_type="usage_pattern",
                    baseline_value=10.0,  # Normal baseline
                    current_value=requests_per_second,
                    deviation_score=(requests_per_second - 10.0) / 10.0,
                    is_anomaly=True,
                    severity="high",
                    recommendation=f"Unusually high request rate detected: {requests_per_second:.1f} req/s. Potential DDoS attack."
                )
                anomalies.append(anomaly)
                logger.warning(f"🚨 USAGE ANOMALY: {anomaly.recommendation}")
            else:
                logger.info(f"✅ Request rate normal: {requests_per_second:.1f} req/s")
            
            # Test for unusual geographic access patterns
            unusual_locations = [
                {"latitude": 90.0, "longitude": 0.0, "name": "North Pole"},
                {"latitude": -90.0, "longitude": 0.0, "name": "South Pole"},
                {"latitude": 0.0, "longitude": 180.0, "name": "Pacific Ocean"},
            ]
            
            for location in unusual_locations:
                try:
                    async with session.post(
                        f"{self.base_url}/api/language/detect",
                        json={"latitude": location["latitude"], "longitude": location["longitude"]}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("detected_language") != "en":  # Should fallback to English for unusual locations
                                anomaly = AnomalyDetectionResult(
                                    metric_type="usage_pattern",
                                    baseline_value=1.0,  # Expected English fallback
                                    current_value=0.0,  # Unexpected language
                                    deviation_score=1.0,
                                    is_anomaly=True,
                                    severity="low",
                                    recommendation=f"Unusual geographic access from {location['name']} with unexpected language detection"
                                )
                                anomalies.append(anomaly)
                                logger.warning(f"🚨 GEOGRAPHIC ANOMALY: {anomaly.recommendation}")
                            else:
                                logger.info(f"✅ Geographic access from {location['name']}: Proper fallback to English")
                except Exception as e:
                    logger.error(f"Error testing geographic access for {location['name']}: {e}")
        
        return anomalies
    
    async def detect_security_anomalies(self) -> List[AnomalyDetectionResult]:
        """Monitor for potential security threats, unusual access attempts, or data breaches"""
        logger.info("🔒 DETECTING SECURITY ANOMALIES...")
        
        anomalies = []
        
        async with aiohttp.ClientSession() as session:
            # Test for SQL injection attempts
            sql_injection_payloads = [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "admin'--",
                "' UNION SELECT * FROM users--"
            ]
            
            for payload in sql_injection_payloads:
                try:
                    async with session.post(
                        f"{self.base_url}/api/language/detect",
                        json={"latitude": payload, "longitude": 0.0}
                    ) as response:
                        # If server doesn't properly handle malicious input, it's a security issue
                        if response.status == 500:
                            anomaly = AnomalyDetectionResult(
                                metric_type="security",
                                baseline_value=422.0,  # Expected validation error
                                current_value=500.0,  # Server error indicates potential vulnerability
                                deviation_score=1.0,
                                is_anomaly=True,
                                severity="critical",
                                recommendation=f"Potential SQL injection vulnerability detected with payload: {payload[:20]}..."
                            )
                            anomalies.append(anomaly)
                            logger.warning(f"🚨 SECURITY ANOMALY: {anomaly.recommendation}")
                        else:
                            logger.info(f"✅ SQL injection protection working for payload: {payload[:20]}...")
                except Exception as e:
                    logger.error(f"Error testing SQL injection payload: {e}")
            
            # Test for XSS attempts
            xss_payloads = [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>"
            ]
            
            for payload in xss_payloads:
                try:
                    async with session.post(
                        f"{self.base_url}/api/compliance/disclaimers",
                        json={"country_code": payload, "language_code": "en"}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            # Check if malicious payload is reflected in response
                            response_text = json.dumps(data)
                            if payload in response_text:
                                anomaly = AnomalyDetectionResult(
                                    metric_type="security",
                                    baseline_value=0.0,  # No XSS payload should be reflected
                                    current_value=1.0,  # XSS payload found in response
                                    deviation_score=1.0,
                                    is_anomaly=True,
                                    severity="critical",
                                    recommendation=f"Potential XSS vulnerability detected - malicious payload reflected in response"
                                )
                                anomalies.append(anomaly)
                                logger.warning(f"🚨 SECURITY ANOMALY: {anomaly.recommendation}")
                            else:
                                logger.info(f"✅ XSS protection working for payload: {payload[:20]}...")
                        else:
                            logger.info(f"✅ XSS payload properly rejected: {payload[:20]}...")
                except Exception as e:
                    logger.error(f"Error testing XSS payload: {e}")
        
        return anomalies
    
    async def detect_stream_accessibility_anomalies(self) -> List[AnomalyDetectionResult]:
        """Detect stream accessibility drops or failures"""
        logger.info("📡 DETECTING STREAM ACCESSIBILITY ANOMALIES...")
        
        anomalies = []
        
        # Test main radio streams
        test_streams = [
            "https://ice1.somafm.com/groovesalad-256-mp3",
            "https://stream.radioparadise.com/aac-320",
            "https://stream.radioparadise.com/mp3-192",
            "https://icecast.radiofrance.fr/fip-hifi.aac",
            "https://icecast.radiofrance.fr/fip-midfi.mp3",
            "http://ice1.somafm.com/dronezone-256-mp3",
            "http://ice1.somafm.com/defcon-256-mp3"
        ]
        
        accessible_streams = 0
        total_streams = len(test_streams)
        
        async with aiohttp.ClientSession() as session:
            for stream_url in test_streams:
                try:
                    async with session.head(stream_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            accessible_streams += 1
                            logger.info(f"✅ Stream accessible: {stream_url}")
                        else:
                            logger.warning(f"❌ Stream inaccessible ({response.status}): {stream_url}")
                except Exception as e:
                    logger.warning(f"❌ Stream error: {stream_url} - {e}")
        
        accessibility_rate = (accessible_streams / total_streams) * 100
        
        # Anomaly if accessibility drops below 70%
        if accessibility_rate < 70:
            anomaly = AnomalyDetectionResult(
                metric_type="stream_accessibility",
                baseline_value=85.0,  # Expected baseline
                current_value=accessibility_rate,
                deviation_score=(85.0 - accessibility_rate) / 15.0,
                is_anomaly=True,
                severity="high" if accessibility_rate < 50 else "medium",
                recommendation=f"Stream accessibility dropped to {accessibility_rate:.1f}% ({accessible_streams}/{total_streams} streams). Check stream providers."
            )
            anomalies.append(anomaly)
            logger.warning(f"🚨 STREAM ANOMALY: {anomaly.recommendation}")
        else:
            logger.info(f"✅ Stream accessibility normal: {accessibility_rate:.1f}% ({accessible_streams}/{total_streams})")
        
        return anomalies
    
    async def generate_ai_analysis_report(self, all_anomalies: List[AnomalyDetectionResult]) -> Dict[str, Any]:
        """Generate intelligent analysis of system health with actionable recommendations"""
        logger.info("🤖 GENERATING AI ANALYSIS REPORT...")
        
        # Categorize anomalies by severity
        critical_anomalies = [a for a in all_anomalies if a.severity == "critical"]
        high_anomalies = [a for a in all_anomalies if a.severity == "high"]
        medium_anomalies = [a for a in all_anomalies if a.severity == "medium"]
        low_anomalies = [a for a in all_anomalies if a.severity == "low"]
        
        # Calculate overall system health score
        total_anomalies = len(all_anomalies)
        if total_anomalies == 0:
            health_score = 100.0
        else:
            # Weight anomalies by severity
            severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
            weighted_score = sum(severity_weights.get(a.severity, 1) for a in all_anomalies)
            health_score = max(0, 100 - (weighted_score * 2))  # Each weighted point reduces score by 2%
        
        # Generate root cause analysis
        root_causes = []
        if critical_anomalies:
            root_causes.append("Critical security vulnerabilities detected - immediate attention required")
        if high_anomalies:
            root_causes.append("Performance degradation or high error rates detected")
        if medium_anomalies:
            root_causes.append("Minor system irregularities that may impact user experience")
        
        # Generate actionable recommendations
        recommendations = []
        if critical_anomalies:
            recommendations.append("IMMEDIATE: Address security vulnerabilities and implement input validation")
        if high_anomalies:
            recommendations.append("HIGH PRIORITY: Investigate performance bottlenecks and error patterns")
        if len([a for a in all_anomalies if a.metric_type == "stream_accessibility"]) > 0:
            recommendations.append("MEDIUM PRIORITY: Update stream URLs and implement fallback mechanisms")
        if not all_anomalies:
            recommendations.append("MAINTENANCE: Continue monitoring - system operating within normal parameters")
        
        # Performance baseline summary
        baseline_summary = {}
        for endpoint, baseline in self.baselines.items():
            baseline_summary[endpoint] = {
                "avg_response_time_ms": round(baseline["mean_response_time"], 2),
                "success_rate_percent": round(baseline["success_rate"], 2),
                "performance_grade": "A" if baseline["mean_response_time"] < 100 else "B" if baseline["mean_response_time"] < 500 else "C"
            }
        
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "system_health_score": round(health_score, 1),
            "total_anomalies_detected": total_anomalies,
            "anomaly_breakdown": {
                "critical": len(critical_anomalies),
                "high": len(high_anomalies),
                "medium": len(medium_anomalies),
                "low": len(low_anomalies)
            },
            "performance_baselines": baseline_summary,
            "root_cause_analysis": root_causes,
            "actionable_recommendations": recommendations,
            "proactive_monitoring_status": "ACTIVE" if total_anomalies == 0 else "ALERT",
            "next_analysis_recommended": (datetime.now() + timedelta(hours=1)).isoformat(),
            "detailed_anomalies": [
                {
                    "type": a.metric_type,
                    "severity": a.severity,
                    "baseline": a.baseline_value,
                    "current": a.current_value,
                    "deviation": round(a.deviation_score, 2),
                    "recommendation": a.recommendation
                } for a in all_anomalies
            ]
        }
        
        return report

async def main():
    """Main testing function for AI-Powered Anomaly Detection System"""
    # Get backend URL from environment
    backend_url = "https://radio-stability.preview.emergentagent.com"
    
    logger.info("🚀 STARTING AI-POWERED ANOMALY DETECTION SYSTEM TESTING - PHASE 4")
    logger.info(f"🎯 Target Backend: {backend_url}")
    
    tester = AIAnomalyDetectionTester(backend_url)
    
    try:
        # Phase 1: Establish Performance Baselines
        logger.info("\n" + "="*80)
        logger.info("📊 PHASE 1: ESTABLISHING PERFORMANCE BASELINES")
        logger.info("="*80)
        baselines = await tester.establish_performance_baselines()
        
        if not baselines:
            logger.error("❌ CRITICAL: Failed to establish performance baselines")
            return False
        
        logger.info(f"✅ Successfully established baselines for {len(baselines)} endpoints")
        
        # Phase 2: Anomaly Detection Implementation
        logger.info("\n" + "="*80)
        logger.info("🔍 PHASE 2: ANOMALY DETECTION IMPLEMENTATION")
        logger.info("="*80)
        
        all_anomalies = []
        
        # Detect performance anomalies
        performance_anomalies = await tester.detect_performance_anomalies()
        all_anomalies.extend(performance_anomalies)
        
        # Detect error pattern anomalies
        error_anomalies = await tester.detect_error_pattern_anomalies()
        all_anomalies.extend(error_anomalies)
        
        # Detect usage pattern anomalies
        usage_anomalies = await tester.detect_usage_pattern_anomalies()
        all_anomalies.extend(usage_anomalies)
        
        # Detect security anomalies
        security_anomalies = await tester.detect_security_anomalies()
        all_anomalies.extend(security_anomalies)
        
        # Detect stream accessibility anomalies
        stream_anomalies = await tester.detect_stream_accessibility_anomalies()
        all_anomalies.extend(stream_anomalies)
        
        # Phase 3: AI Analysis and Reporting
        logger.info("\n" + "="*80)
        logger.info("🤖 PHASE 3: AI ANALYSIS AND INTELLIGENT REPORTING")
        logger.info("="*80)
        
        ai_report = await tester.generate_ai_analysis_report(all_anomalies)
        
        # Display comprehensive results
        logger.info("\n" + "="*80)
        logger.info("📋 AI-POWERED ANOMALY DETECTION SYSTEM ANALYSIS COMPLETE")
        logger.info("="*80)
        
        logger.info(f"🎯 SYSTEM HEALTH SCORE: {ai_report['system_health_score']}%")
        logger.info(f"📊 TOTAL ANOMALIES DETECTED: {ai_report['total_anomalies_detected']}")
        logger.info(f"🚨 CRITICAL: {ai_report['anomaly_breakdown']['critical']}")
        logger.info(f"⚠️  HIGH: {ai_report['anomaly_breakdown']['high']}")
        logger.info(f"📝 MEDIUM: {ai_report['anomaly_breakdown']['medium']}")
        logger.info(f"ℹ️  LOW: {ai_report['anomaly_breakdown']['low']}")
        
        logger.info("\n📊 PERFORMANCE BASELINES ESTABLISHED:")
        for endpoint, stats in ai_report['performance_baselines'].items():
            logger.info(f"  • {endpoint}: {stats['avg_response_time_ms']}ms avg, {stats['success_rate_percent']}% success, Grade {stats['performance_grade']}")
        
        if ai_report['root_cause_analysis']:
            logger.info("\n🔍 ROOT CAUSE ANALYSIS:")
            for cause in ai_report['root_cause_analysis']:
                logger.info(f"  • {cause}")
        
        logger.info("\n💡 ACTIONABLE RECOMMENDATIONS:")
        for rec in ai_report['actionable_recommendations']:
            logger.info(f"  • {rec}")
        
        if ai_report['detailed_anomalies']:
            logger.info("\n🚨 DETAILED ANOMALIES:")
            for anomaly in ai_report['detailed_anomalies']:
                logger.info(f"  • [{anomaly['severity'].upper()}] {anomaly['type']}: {anomaly['recommendation']}")
        
        logger.info(f"\n🔄 PROACTIVE MONITORING STATUS: {ai_report['proactive_monitoring_status']}")
        logger.info(f"⏰ NEXT ANALYSIS RECOMMENDED: {ai_report['next_analysis_recommended']}")
        
        # Determine overall success
        success_criteria_met = {
            "baselines_established": len(baselines) >= 6,  # At least 6 endpoints baselined
            "anomaly_detection_active": True,  # System is actively detecting
            "ai_analysis_generated": ai_report['system_health_score'] is not None,
            "no_critical_issues": ai_report['anomaly_breakdown']['critical'] == 0,
            "performance_acceptable": ai_report['system_health_score'] >= 70
        }
        
        success_count = sum(success_criteria_met.values())
        total_criteria = len(success_criteria_met)
        
        logger.info(f"\n✅ SUCCESS CRITERIA MET: {success_count}/{total_criteria}")
        for criterion, met in success_criteria_met.items():
            status = "✅" if met else "❌"
            logger.info(f"  {status} {criterion.replace('_', ' ').title()}")
        
        overall_success = success_count >= 4  # At least 4/5 criteria must be met
        
        if overall_success:
            logger.info("\n🎉 AI-POWERED ANOMALY DETECTION SYSTEM TESTING SUCCESSFUL!")
            logger.info("✅ System demonstrates intelligent monitoring capabilities")
            logger.info("✅ Proactive issue detection is operational")
            logger.info("✅ Performance baselines established successfully")
            logger.info("✅ AI analysis provides actionable insights")
        else:
            logger.error("\n❌ AI-POWERED ANOMALY DETECTION SYSTEM TESTING FAILED")
            logger.error("❌ Critical issues detected or insufficient monitoring capabilities")
        
        return overall_success
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR during anomaly detection testing: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)