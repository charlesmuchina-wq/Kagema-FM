"""
Content Compliance Engine for Dragon KARAU AI
Task 24: Automated content filtering, policy enforcement, compliance checks
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import re
from bson import ObjectId

load_dotenv()
logger = logging.getLogger(__name__)


class ContentComplianceEngine:
    """Automated content compliance and policy enforcement"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Compliance rules
        self.prohibited_keywords = [
            'hate', 'violence', 'explicit', 'illegal', 'drugs',
            'terrorism', 'extremism', 'scam', 'fraud'
        ]
        
        self.content_ratings = {
            'general': {'min_age': 0, 'restrictions': []},
            'pg': {'min_age': 7, 'restrictions': ['mild_language']},
            'pg13': {'min_age': 13, 'restrictions': ['moderate_language', 'suggestive_themes']},
            'mature': {'min_age': 18, 'restrictions': ['strong_language', 'adult_themes']},
            'explicit': {'min_age': 21, 'restrictions': ['explicit_content', 'adult_only']}
        }
        
        logger.info("Content Compliance Engine initialized")
    
    async def run_compliance_cycle(self) -> Dict[str, Any]:
        """Run complete compliance checking cycle"""
        start_time = datetime.utcnow()
        
        logger.info("🔒 Starting Content Compliance Cycle")
        
        results = {
            'timestamp': start_time.isoformat(),
            'checks': {},
            'actions': []
        }
        
        # Run compliance checks
        results['checks']['station_content'] = await self.check_station_content_compliance()
        results['checks']['metadata_validation'] = await self.validate_station_metadata()
        results['checks']['policy_enforcement'] = await self.enforce_content_policies()
        results['checks']['age_restrictions'] = await self.verify_age_restrictions()
        
        # Generate compliance report
        results['report'] = await self.generate_compliance_report()
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        results['execution_time_seconds'] = duration
        results['status'] = 'completed'
        
        # Store compliance check results
        await self.db.compliance_history.insert_one(results.copy())
        
        logger.info(f"✅ Compliance Cycle Complete: {duration:.2f}s")
        
        return results
    
    async def check_station_content_compliance(self) -> Dict[str, Any]:
        """Check all stations for content compliance"""
        try:
            stations = await self.db.radio_stations.find({}).to_list(length=10000)
            
            compliant = 0
            non_compliant = 0
            flagged = []
            
            for station in stations:
                compliance_check = await self._check_station_compliance(station)
                
                if compliance_check['compliant']:
                    compliant += 1
                else:
                    non_compliant += 1
                    flagged.append({
                        'station_id': str(station['_id']),
                        'name': station.get('name'),
                        'issues': compliance_check['issues']
                    })
                    
                    # Update station with compliance status
                    await self.db.radio_stations.update_one(
                        {'_id': station['_id']},
                        {'$set': {
                            'compliance_status': 'non_compliant',
                            'compliance_issues': compliance_check['issues'],
                            'compliance_checked_at': datetime.utcnow()
                        }}
                    )
            
            return {
                'status': 'success',
                'total_checked': len(stations),
                'compliant': compliant,
                'non_compliant': non_compliant,
                'flagged_stations': flagged[:10]  # Top 10 issues
            }
            
        except Exception as e:
            logger.error(f"Content compliance check error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _check_station_compliance(self, station: Dict[str, Any]) -> Dict[str, Any]:
        """Check individual station compliance"""
        issues = []
        
        # Check name for prohibited content
        name = station.get('name', '').lower()
        for keyword in self.prohibited_keywords:
            if keyword in name:
                issues.append(f"Prohibited keyword '{keyword}' in station name")
        
        # Check description
        description = station.get('description', '').lower()
        for keyword in self.prohibited_keywords:
            if keyword in description:
                issues.append(f"Prohibited keyword '{keyword}' in description")
        
        # Check URL validity
        stream_url = station.get('stream_url', '')
        if not stream_url or not self._is_valid_url(stream_url):
            issues.append("Invalid or missing stream URL")
        
        # Check if station has required metadata
        required_fields = ['name', 'country', 'language']
        for field in required_fields:
            if not station.get(field):
                issues.append(f"Missing required field: {field}")
        
        return {
            'compliant': len(issues) == 0,
            'issues': issues
        }
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    async def validate_station_metadata(self) -> Dict[str, Any]:
        """Validate station metadata quality"""
        try:
            stations = await self.db.radio_stations.find({}).to_list(length=10000)
            
            valid = 0
            invalid = 0
            
            for station in stations:
                # Check metadata completeness
                completeness_score = 0
                total_fields = 8
                
                if station.get('name'): completeness_score += 1
                if station.get('country'): completeness_score += 1
                if station.get('language'): completeness_score += 1
                if station.get('genre'): completeness_score += 1
                if station.get('description'): completeness_score += 1
                if station.get('stream_url'): completeness_score += 1
                if station.get('website'): completeness_score += 1
                if station.get('logo_url'): completeness_score += 1
                
                score = (completeness_score / total_fields) * 100
                
                if score >= 60:
                    valid += 1
                else:
                    invalid += 1
                
                # Update metadata quality score
                await self.db.radio_stations.update_one(
                    {'_id': station['_id']},
                    {'$set': {'metadata_quality_score': round(score, 2)}}
                )
            
            return {
                'status': 'success',
                'total_validated': len(stations),
                'valid_metadata': valid,
                'invalid_metadata': invalid,
                'quality_threshold': 60
            }
            
        except Exception as e:
            logger.error(f"Metadata validation error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def enforce_content_policies(self) -> Dict[str, Any]:
        """Enforce content policies across all stations"""
        try:
            # Get all non-compliant stations
            non_compliant = await self.db.radio_stations.find({
                'compliance_status': 'non_compliant'
            }).to_list(length=1000)
            
            actions_taken = []
            
            for station in non_compliant:
                issues = station.get('compliance_issues', [])
                
                # Determine action based on severity
                if any('prohibited keyword' in issue.lower() for issue in issues):
                    # Flag for review
                    await self.db.radio_stations.update_one(
                        {'_id': station['_id']},
                        {'$set': {
                            'status': 'flagged',
                            'flagged_at': datetime.utcnow(),
                            'flag_reason': 'Content policy violation'
                        }}
                    )
                    actions_taken.append({
                        'station_id': str(station['_id']),
                        'action': 'flagged',
                        'reason': 'Prohibited content detected'
                    })
                
                elif len(issues) >= 3:
                    # Suspend station if multiple issues
                    await self.db.radio_stations.update_one(
                        {'_id': station['_id']},
                        {'$set': {
                            'status': 'suspended',
                            'suspended_at': datetime.utcnow(),
                            'suspension_reason': 'Multiple compliance violations'
                        }}
                    )
                    actions_taken.append({
                        'station_id': str(station['_id']),
                        'action': 'suspended',
                        'reason': f'{len(issues)} violations'
                    })
            
            return {
                'status': 'success',
                'stations_processed': len(non_compliant),
                'actions_taken': len(actions_taken),
                'details': actions_taken[:10]
            }
            
        except Exception as e:
            logger.error(f"Policy enforcement error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def verify_age_restrictions(self) -> Dict[str, Any]:
        """Verify age restriction compliance"""
        try:
            # Check stations with mature/explicit content
            mature_stations = await self.db.radio_stations.find({
                'content_rating': {'$in': ['mature', 'explicit']}
            }).to_list(length=1000)
            
            verified = 0
            needs_review = 0
            
            for station in mature_stations:
                rating = station.get('content_rating', 'general')
                rating_info = self.content_ratings.get(rating, {})
                
                # Verify age gate is properly set
                has_age_gate = station.get('age_verification_required', False)
                min_age = rating_info.get('min_age', 0)
                
                if has_age_gate and min_age >= 18:
                    verified += 1
                else:
                    needs_review += 1
                    # Update to require age verification
                    await self.db.radio_stations.update_one(
                        {'_id': station['_id']},
                        {'$set': {
                            'age_verification_required': True,
                            'minimum_age': min_age
                        }}
                    )
            
            return {
                'status': 'success',
                'mature_stations_total': len(mature_stations),
                'verified': verified,
                'updated': needs_review
            }
            
        except Exception as e:
            logger.error(f"Age restriction verification error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            total_stations = await self.db.radio_stations.count_documents({})
            compliant = await self.db.radio_stations.count_documents({'compliance_status': {'$ne': 'non_compliant'}})
            non_compliant = await self.db.radio_stations.count_documents({'compliance_status': 'non_compliant'})
            flagged = await self.db.radio_stations.count_documents({'status': 'flagged'})
            suspended = await self.db.radio_stations.count_documents({'status': 'suspended'})
            
            compliance_rate = (compliant / total_stations * 100) if total_stations > 0 else 0
            
            return {
                'status': 'success',
                'total_stations': total_stations,
                'compliant': compliant,
                'non_compliant': non_compliant,
                'flagged': flagged,
                'suspended': suspended,
                'compliance_rate_percent': round(compliance_rate, 2),
                'health': 'good' if compliance_rate >= 90 else 'needs_attention'
            }
            
        except Exception as e:
            logger.error(f"Compliance report error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def rate_content(self, station_id: str, rating: str) -> Dict[str, Any]:
        """Rate station content"""
        try:
            if rating not in self.content_ratings:
                return {'status': 'error', 'error': f'Invalid rating: {rating}'}
            
            rating_info = self.content_ratings[rating]
            
            await self.db.radio_stations.update_one(
                {'_id': ObjectId(station_id)},
                {'$set': {
                    'content_rating': rating,
                    'minimum_age': rating_info['min_age'],
                    'content_restrictions': rating_info['restrictions'],
                    'rated_at': datetime.utcnow()
                }}
            )
            
            return {'status': 'success', 'rating': rating, 'rating_info': rating_info}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def get_compliance_stats(self) -> Dict[str, Any]:
        """Get compliance statistics"""
        try:
            stats = await self.generate_compliance_report()
            
            # Add recent violations
            recent_violations = await self.db.radio_stations.find({
                'compliance_status': 'non_compliant',
                'compliance_checked_at': {'$gte': datetime.utcnow() - timedelta(days=7)}
            }).sort('compliance_checked_at', -1).limit(10).to_list(length=10)
            
            stats['recent_violations'] = [{
                'station_id': str(v['_id']),
                'name': v.get('name'),
                'issues': v.get('compliance_issues', []),
                'checked_at': v.get('compliance_checked_at').isoformat() if v.get('compliance_checked_at') else None
            } for v in recent_violations]
            
            return stats
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


def get_content_compliance_engine():
    """Get singleton compliance engine instance"""
    global _compliance_engine
    if '_compliance_engine' not in globals():
        globals()['_compliance_engine'] = ContentComplianceEngine()
    return globals()['_compliance_engine']
