"""AI Radio Intelligence Bot
Advanced autonomous system for radio station validation, discovery, and auto-healing
Uses OpenAI GPT-4o-mini, Radio Browser API, and geolocation intelligence
"""
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

logger = logging.getLogger(__name__)

class AIRadioIntelligenceBot:
    """Autonomous AI-powered radio station maintenance system"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Statistics tracking
        self.stats = {
            'total_validations': 0,
            'broken_links_detected': 0,
            'auto_replacements': 0,
            'ai_discoveries': 0,
            'failed_validations': 0,
            'compromised_urls_detected': 0
        }
        
        # Radio Browser API
        self.radio_browser_api = 'https://de1.api.radio-browser.info/json'
        
        # OpenAI API key (optional - will use mocked responses if not available)
        self.openai_api_key = os.getenv('OPENAI_API_KEY', os.getenv('EMERGENT_LLM_KEY', ''))
        self.use_ai = bool(self.openai_api_key)
        
        self.status = 'operational'
        
        logger.info(f"AI Radio Intelligence Bot initialized (AI: {'enabled' if self.use_ai else 'disabled'})")
    
    async def validate_station(self, station: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single radio station's health status"""
        self.stats['total_validations'] += 1
        
        station_id = station.get('id', str(station.get('_id', 'unknown')))
        stream_url = station.get('stream_url', '')
        
        try:
            # Check if URL is compromised
            if self._is_compromised_url(stream_url):
                self.stats['compromised_urls_detected'] += 1
                return {
                    'station_id': station_id,
                    'health_status': 'COMPROMISED',
                    'accessible': False,
                    'status_code': None,
                    'validated_at': datetime.utcnow()
                }
            
            # Check URL accessibility
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                try:
                    async with session.head(stream_url, allow_redirects=True) as response:
                        status_code = response.status
                        
                        if status_code == 200:
                            health_status = 'OPERATIONAL'
                            accessible = True
                        elif 300 <= status_code < 400:
                            health_status = 'OPERATIONAL'  # Redirects are OK
                            accessible = True
                        elif status_code == 404:
                            health_status = 'BROKEN_LINK'
                            accessible = False
                            self.stats['broken_links_detected'] += 1
                        elif status_code == 403:
                            health_status = 'FORBIDDEN'
                            accessible = False
                            self.stats['broken_links_detected'] += 1
                        elif status_code >= 500:
                            health_status = 'DEGRADED'
                            accessible = False
                            self.stats['broken_links_detected'] += 1
                        else:
                            health_status = 'UNKNOWN'
                            accessible = False
                        
                        # Update station in database
                        await self.db.radio_stations.update_one(
                            {'_id': station['_id']},
                            {
                                '$set': {
                                    'health_status': health_status,
                                    'last_validated': datetime.utcnow(),
                                    'stream_accessible': accessible
                                }
                            }
                        )
                        
                        return {
                            'station_id': station_id,
                            'health_status': health_status,
                            'accessible': accessible,
                            'status_code': status_code,
                            'validated_at': datetime.utcnow()
                        }
                except asyncio.TimeoutError:
                    self.stats['broken_links_detected'] += 1
                    await self.db.radio_stations.update_one(
                        {'_id': station['_id']},
                        {
                            '$set': {
                                'health_status': 'BROKEN_LINK',
                                'last_validated': datetime.utcnow(),
                                'stream_accessible': False
                            }
                        }
                    )
                    return {
                        'station_id': station_id,
                        'health_status': 'BROKEN_LINK',
                        'accessible': False,
                        'status_code': None,
                        'error': 'timeout',
                        'validated_at': datetime.utcnow()
                    }
                except Exception as e:
                    self.stats['failed_validations'] += 1
                    logger.error(f"Validation error for {station_id}: {e}")
                    return {
                        'station_id': station_id,
                        'health_status': 'UNUSABLE',
                        'accessible': False,
                        'error': str(e),
                        'validated_at': datetime.utcnow()
                    }
        except Exception as e:
            self.stats['failed_validations'] += 1
            logger.error(f"Station validation failed: {e}")
            return {
                'station_id': station_id,
                'health_status': 'ERROR',
                'error': str(e),
                'validated_at': datetime.utcnow()
            }
    
    def _is_compromised_url(self, url: str) -> bool:
        """Detect suspicious or compromised URLs"""
        # Suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq']
        for tld in suspicious_tlds:
            if tld in url.lower():
                return True
        
        # Direct IP addresses
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        if re.search(ip_pattern, url):
            return True
        
        # URL shorteners
        shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co']
        for shortener in shorteners:
            if shortener in url.lower():
                return True
        
        # Unusually long URLs
        if len(url) > 300:
            return True
        
        return False
    
    async def discover_replacement_radio_browser(self, station: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover replacement stations using Radio Browser API"""
        country = station.get('country', '')
        genre = station.get('genre', '')
        
        try:
            async with aiohttp.ClientSession() as session:
                # Search by country
                url = f"{self.radio_browser_api}/stations/bycountrycodeexact/{country}"
                params = {'limit': 5, 'hidebroken': 'true', 'order': 'votes', 'reverse': 'true'}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        replacements = []
                        for item in data[:5]:  # Top 5 matches
                            confidence = self._calculate_replacement_confidence(station, item)
                            replacements.append({
                                'name': item.get('name', 'Unknown'),
                                'stream_url': item.get('url', ''),
                                'country': item.get('countrycode', ''),
                                'genre': item.get('tags', ''),
                                'confidence': confidence,
                                'source': 'radio_browser',
                                'reasoning': f"Match based on country ({country}) and votes ({item.get('votes', 0)})"
                            })
                        
                        return replacements
        except Exception as e:
            logger.error(f"Radio Browser discovery error: {e}")
        
        return []
    
    async def discover_replacement_multi_source(self, station: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover replacement stations from multiple sources"""
        all_replacements = []
        
        # Source 1: Radio Browser API
        radio_browser_results = await self.discover_replacement_radio_browser(station)
        all_replacements.extend(radio_browser_results)
        
        # Source 2: Radio Garden (if country is major)
        try:
            from radio_garden_crawler import get_radio_garden_crawler
            
            country = station.get('country', '')
            major_countries = ['GB', 'US', 'FR', 'DE', 'JP', 'KE', 'AU', 'IN', 'BR', 'NG']
            
            if country in major_countries:
                # Radio Garden can provide alternatives
                logger.info(f"Searching Radio Garden for {country} stations")
                # Note: Would need to implement search endpoint
        except Exception as e:
            logger.error(f"Radio Garden discovery error: {e}")
        
        return all_replacements
    
    async def discover_replacement_ai(self, station: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use OpenAI to intelligently discover replacement station"""
        if not self.use_ai:
            return None
        
        try:
            prompt = f"""You are an expert radio station discovery AI. A radio station needs replacement.

Station Details:
- Name: {station.get('name', 'Unknown')}
- Country: {station.get('country', 'Unknown')}
- Genre: {station.get('genre', 'General')}
- Language: {station.get('language', 'en')}

Task: Find a similar radio station that matches these characteristics. Provide the station name, a working stream URL, your reasoning, and confidence score (0-100).

Output as JSON: {{"name": "...", "stream_url": "...", "reasoning": "...", "confidence": 85}}
"""
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.openai_api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'model': 'gpt-4o-mini',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.7,
                    'max_tokens': 500
                }
                
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        # Parse JSON from response
                        try:
                            result = json.loads(content)
                            result['source'] = 'openai_ai'
                            self.stats['ai_discoveries'] += 1
                            return result
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse AI response: {content}")
        except Exception as e:
            logger.error(f"OpenAI discovery error: {e}")
        
        return None
    
    def _calculate_replacement_confidence(self, original: Dict, candidate: Dict) -> int:
        """Calculate confidence score for replacement station"""
        score = 50  # Base score
        
        # Country match
        if original.get('country', '').upper() == candidate.get('countrycode', '').upper():
            score += 20
        
        # Genre similarity
        original_genre = original.get('genre', '').lower()
        candidate_tags = candidate.get('tags', '').lower()
        if original_genre and original_genre in candidate_tags:
            score += 15
        
        # Vote popularity bonus
        votes = candidate.get('votes', 0)
        if votes >= 100:
            score += 10
        elif votes >= 50:
            score += 5
        
        # Bitrate quality
        bitrate = candidate.get('bitrate', 0)
        if bitrate >= 128:
            score += 5
        
        return min(100, score)
    
    async def heal_station(self, station: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to heal a broken or compromised station"""
        station_id = station.get('id', str(station.get('_id', 'unknown')))
        
        logger.info(f"Attempting to heal station: {station_id}")
        
        # Step 1: Try multi-source discovery (Radio Browser + Radio Garden)
        replacements = await self.discover_replacement_multi_source(station)
        
        # Step 2: If no results, try AI
        if not replacements and self.use_ai:
            ai_result = await self.discover_replacement_ai(station)
            if ai_result:
                replacements = [ai_result]
        
        # Step 3: Validate and select best replacement
        if replacements:
            for replacement in sorted(replacements, key=lambda x: x.get('confidence', 0), reverse=True):
                # Validate the replacement URL
                test_station = {'stream_url': replacement['stream_url'], 'id': 'test', '_id': 'test'}
                validation = await self.validate_station(test_station)
                
                if validation.get('accessible', False):
                    # Apply the replacement
                    await self.db.radio_stations.update_one(
                        {'_id': station['_id']},
                        {
                            '$set': {
                                'stream_url': replacement['stream_url'],
                                'health_status': 'OPERATIONAL',
                                'last_validated': datetime.utcnow(),
                                'stream_accessible': True,
                                'healed_at': datetime.utcnow(),
                                'healing_source': replacement.get('source', 'unknown')
                            },
                            '$inc': {'replacement_count': 1}
                        }
                    )
                    
                    self.stats['auto_replacements'] += 1
                    
                    logger.info(f"Successfully healed {station_id} with {replacement['stream_url']}")
                    
                    return {
                        'status': 'healed',
                        'station_id': station_id,
                        'new_url': replacement['stream_url'],
                        'confidence': replacement.get('confidence', 0),
                        'reasoning': replacement.get('reasoning', 'No reasoning provided'),
                        'source': replacement.get('source', 'unknown')
                    }
        
        logger.warning(f"Failed to heal station: {station_id}")
        return {
            'status': 'failed',
            'station_id': station_id,
            'message': 'No suitable replacement found'
        }
    
    async def scan_all_stations(self) -> Dict[str, Any]:
        """Perform comprehensive scan of all registered stations"""
        logger.info("Starting comprehensive station scan...")
        
        stations = await self.db.radio_stations.find({}).to_list(length=None)
        
        results = {
            'total_stations': len(stations),
            'operational': 0,
            'broken': 0,
            'compromised': 0,
            'healed': 0,
            'failed_to_heal': 0,
            'stations_details': []
        }
        
        for station in stations:
            # Validate station
            validation = await self.validate_station(station)
            
            if validation['health_status'] in ['BROKEN_LINK', 'COMPROMISED', 'UNUSABLE', 'FORBIDDEN']:
                results['broken'] += 1
                
                # Attempt auto-healing
                heal_result = await self.heal_station(station)
                
                if heal_result['status'] == 'healed':
                    results['healed'] += 1
                    results['operational'] += 1
                else:
                    results['failed_to_heal'] += 1
            elif validation['health_status'] == 'OPERATIONAL':
                results['operational'] += 1
            
            results['stations_details'].append(validation)
        
        logger.info(f"Scan complete: {results['operational']}/{results['total_stations']} operational")
        
        return results
    
    async def get_status(self) -> Dict[str, Any]:
        """Get bot status and statistics"""
        total_stations = await self.db.radio_stations.count_documents({})
        operational = await self.db.radio_stations.count_documents({'health_status': 'OPERATIONAL'})
        broken = await self.db.radio_stations.count_documents({
            'health_status': {'$in': ['BROKEN_LINK', 'UNUSABLE', 'FORBIDDEN']}
        })
        compromised = await self.db.radio_stations.count_documents({'health_status': 'COMPROMISED'})
        
        return {
            'status': self.status,
            'ai_enabled': self.use_ai,
            'statistics': {
                **self.stats,
                'registered_stations': total_stations,
                'operational_stations': operational,
                'broken_stations': broken,
                'compromised_stations': compromised
            }
        }
    
    async def get_all_stations(self) -> List[Dict[str, Any]]:
        """Get all registered stations with their health status"""
        stations = await self.db.radio_stations.find({}).to_list(length=None)
        
        return [
            {
                'station_id': s.get('id', str(s.get('_id', ''))),
                'name': s.get('name', 'Unknown'),
                'url': s.get('stream_url', ''),
                'country': s.get('country', 'Unknown'),
                'genre': s.get('genre', 'general'),
                'language': s.get('language', 'en'),
                'health_status': s.get('health_status', 'UNKNOWN'),
                'last_validated': s.get('last_validated'),
                'replacement_count': s.get('replacement_count', 0)
            }
            for s in stations
        ]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get healing bot statistics"""
        try:
            total_stations = await self.db.radio_stations.count_documents({})
            healed_stations = await self.db.radio_stations.count_documents({'replacement_count': {'$gt': 0}})
            
            return {
                'total_stations': total_stations,
                'healed_stations': healed_stations,
                'success_rate': round((healed_stations / total_stations * 100), 2) if total_stations > 0 else 0.0,
                'active': True
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                'total_stations': 0,
                'healed_stations': 0,
                'success_rate': 0.0,
                'active': False
            }


# Global bot instance
bot_instance: Optional[AIRadioIntelligenceBot] = None


def get_bot() -> AIRadioIntelligenceBot:
    """Get or create bot instance"""
    global bot_instance
    if bot_instance is None:
        bot_instance = AIRadioIntelligenceBot()
    return bot_instance
