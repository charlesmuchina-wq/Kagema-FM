"""Automated Testing Orchestrator
Runs automated tests for backend and frontend, triggers fixes, and manages system health
"""
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

logger = logging.getLogger(__name__)


class AutomatedTestingOrchestrator:
    """Orchestrates automated testing, healing, and system maintenance"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        self.backend_url = 'http://localhost:8001'
        self.frontend_url = 'http://localhost:3000'
        
        # Test results
        self.test_results = {
            'backend': [],
            'frontend': [],
            'system': []
        }
        
        # Health status
        self.health_status = {
            'backend': 'unknown',
            'frontend': 'unknown',
            'database': 'unknown',
            'overall': 'unknown'
        }
        
        logger.info("Automated Testing Orchestrator initialized")
    
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Run complete automated test suite"""
        logger.info("🔍 Starting full automated test suite...")
        
        start_time = datetime.utcnow()
        results = {
            'started_at': start_time.isoformat(),
            'tests': {}
        }
        
        # 1. Backend API Tests
        logger.info("Testing backend APIs...")
        backend_result = await self.test_backend_apis()
        results['tests']['backend'] = backend_result
        
        # 2. Database Health Tests
        logger.info("Testing database health...")
        db_result = await self.test_database_health()
        results['tests']['database'] = db_result
        
        # 3. Frontend Health Test
        logger.info("Testing frontend health...")
        frontend_result = await self.test_frontend_health()
        results['tests']['frontend'] = frontend_result
        
        # 4. Integration Tests
        logger.info("Testing integrations...")
        integration_result = await self.test_integrations()
        results['tests']['integrations'] = integration_result
        
        # Calculate overall status
        all_passed = all([
            backend_result['status'] == 'passed',
            db_result['status'] == 'passed',
            frontend_result['status'] == 'passed',
            integration_result['status'] == 'passed'
        ])
        
        results['overall_status'] = 'passed' if all_passed else 'failed'
        results['completed_at'] = datetime.utcnow().isoformat()
        results['duration_seconds'] = (datetime.utcnow() - start_time).total_seconds()
        
        # Save results
        await self.db.test_results.insert_one(results)
        
        # Trigger fixes if needed
        if not all_passed:
            await self.trigger_fixes(results)
        
        return results
    
    async def test_backend_apis(self) -> Dict[str, Any]:
        """Test backend API endpoints"""
        endpoints_to_test = [
            {'path': '/api/', 'method': 'GET', 'expected_status': 200},
            {'path': '/api/stations?limit=5', 'method': 'GET', 'expected_status': 200},
            {'path': '/api/crawler/stats', 'method': 'GET', 'expected_status': 200},
            {'path': '/api/call-signs/stats', 'method': 'GET', 'expected_status': 200},
            {'path': '/api/stations/formatting-stats', 'method': 'GET', 'expected_status': 200},
            {'path': '/api/divisions/countries', 'method': 'GET', 'expected_status': 200},
        ]
        
        passed = 0
        failed = 0
        errors = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints_to_test:
                    try:
                        async with session.request(
                            endpoint['method'],
                            f"{self.backend_url}{endpoint['path']}",
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == endpoint['expected_status']:
                                passed += 1
                            else:
                                failed += 1
                                errors.append(f"{endpoint['path']} returned {response.status}")
                    except Exception as e:
                        failed += 1
                        errors.append(f"{endpoint['path']}: {str(e)}")
            
            return {
                'status': 'passed' if failed == 0 else 'failed',
                'passed': passed,
                'failed': failed,
                'total': len(endpoints_to_test),
                'errors': errors
            }
        
        except Exception as e:
            logger.error(f"Backend API testing error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'passed': 0,
                'failed': len(endpoints_to_test)
            }
    
    async def test_database_health(self) -> Dict[str, Any]:
        """Test database connectivity and health"""
        try:
            # Test connection
            await self.db.command('ping')
            
            # Check collections
            collections = await self.db.list_collection_names()
            
            # Check station count
            station_count = await self.db.radio_stations.count_documents({})
            
            # Check indexes
            indexes = await self.db.radio_stations.list_indexes().to_list(length=100)
            
            return {
                'status': 'passed',
                'collections': len(collections),
                'station_count': station_count,
                'indexes': len(indexes),
                'healthy': True
            }
        
        except Exception as e:
            logger.error(f"Database health test error: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'healthy': False
            }
    
    async def test_frontend_health(self) -> Dict[str, Any]:
        """Test frontend availability"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.frontend_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return {
                        'status': 'passed' if response.status == 200 else 'failed',
                        'response_code': response.status,
                        'available': response.status == 200
                    }
        
        except Exception as e:
            logger.error(f"Frontend health test error: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'available': False
            }
    
    async def test_integrations(self) -> Dict[str, Any]:
        """Test system integrations"""
        tests_passed = 0
        tests_failed = 0
        
        # Test crawler integration
        try:
            from dragon_ai_crawler_system import get_crawler
            crawler = get_crawler()
            status = await crawler.get_status()
            tests_passed += 1
        except Exception as e:
            logger.error(f"Crawler integration test failed: {e}")
            tests_failed += 1
        
        # Test healing bot integration
        try:
            from ai_radio_intelligence_bot import get_bot
            bot = get_bot()
            stats = await bot.get_statistics()
            tests_passed += 1
        except Exception as e:
            logger.error(f"Healing bot integration test failed: {e}")
            tests_failed += 1
        
        return {
            'status': 'passed' if tests_failed == 0 else 'failed',
            'passed': tests_passed,
            'failed': tests_failed
        }
    
    async def trigger_fixes(self, test_results: Dict[str, Any]) -> None:
        """Trigger automated fixes based on test results"""
        logger.info("🔧 Triggering automated fixes...")
        
        # Check backend failures
        if test_results['tests']['backend']['status'] == 'failed':
            await self.fix_backend_issues()
        
        # Check frontend failures
        if test_results['tests']['frontend']['status'] == 'failed':
            await self.fix_frontend_issues()
        
        # Check database failures
        if test_results['tests']['database']['status'] == 'failed':
            await self.fix_database_issues()
    
    async def fix_backend_issues(self) -> None:
        """Attempt to fix backend issues"""
        logger.info("Restarting backend service...")
        try:
            subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], check=True)
            await asyncio.sleep(5)  # Wait for restart
            logger.info("Backend restarted successfully")
        except Exception as e:
            logger.error(f"Backend restart failed: {e}")
    
    async def fix_frontend_issues(self) -> None:
        """Attempt to fix frontend issues"""
        logger.info("Restarting frontend service...")
        try:
            subprocess.run(['sudo', 'supervisorctl', 'restart', 'expo'], check=True)
            await asyncio.sleep(10)  # Wait for restart
            logger.info("Frontend restarted successfully")
        except Exception as e:
            logger.error(f"Frontend restart failed: {e}")
    
    async def fix_database_issues(self) -> None:
        """Attempt to fix database issues"""
        logger.info("Checking database connection...")
        try:
            # Attempt to reconnect
            self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
            await self.mongo_client.admin.command('ping')
            logger.info("Database connection restored")
        except Exception as e:
            logger.error(f"Database fix failed: {e}")
    
    async def restart_all_services(self) -> Dict[str, Any]:
        """Restart all system services"""
        logger.info("🔄 Restarting all services...")
        
        results = {
            'backend': False,
            'frontend': False
        }
        
        # Restart backend
        try:
            subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], check=True)
            results['backend'] = True
            logger.info("✅ Backend restarted")
        except Exception as e:
            logger.error(f"❌ Backend restart failed: {e}")
        
        await asyncio.sleep(5)
        
        # Restart frontend
        try:
            subprocess.run(['sudo', 'supervisorctl', 'restart', 'expo'], check=True)
            results['frontend'] = True
            logger.info("✅ Frontend restarted")
        except Exception as e:
            logger.error(f"❌ Frontend restart failed: {e}")
        
        return results
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        # Quick health checks
        backend_health = await self.quick_health_check(f"{self.backend_url}/api/")
        frontend_health = await self.quick_health_check(self.frontend_url)
        
        try:
            await self.db.command('ping')
            db_health = True
        except:
            db_health = False
        
        overall = backend_health and frontend_health and db_health
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'backend': 'healthy' if backend_health else 'unhealthy',
            'frontend': 'healthy' if frontend_health else 'unhealthy',
            'database': 'healthy' if db_health else 'unhealthy',
            'overall': 'healthy' if overall else 'unhealthy'
        }
    
    async def quick_health_check(self, url: str) -> bool:
        """Quick health check for a URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except:
            return False


# Global instance
testing_orchestrator_instance = None


def get_testing_orchestrator() -> AutomatedTestingOrchestrator:
    """Get or create testing orchestrator instance"""
    global testing_orchestrator_instance
    if testing_orchestrator_instance is None:
        testing_orchestrator_instance = AutomatedTestingOrchestrator()
    return testing_orchestrator_instance
