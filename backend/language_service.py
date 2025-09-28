from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass
from cachetools import TTLCache
import logging

logger = logging.getLogger(__name__)

@dataclass
class LanguageInfo:
    code: str
    name: str
    native_name: str
    region: str
    radio_streams: List[str]
    tts_code: str

@dataclass 
class LocationLanguageMapping:
    county: str
    primary_language: str
    secondary_languages: List[str]
    coordinates: Tuple[float, float]  # (latitude, longitude)
    radius_km: float

class GeolocationLanguageService:
    def __init__(self):
        self.cache = TTLCache(maxsize=500, ttl=3600)  # 1 hour cache
        
        # Define supported languages in Kenya
        self.languages = {
            'en': LanguageInfo(
                code='en',
                name='English',
                native_name='English',
                region='National',
                radio_streams=[
                    'http://ice1.somafm.com/groovesalad-256-mp3',  # Default stream
                    'https://radio.garden/api/ara/content/listen/english-kenya/channel.mp3'
                ],
                tts_code='en-KE'
            ),
            'sw': LanguageInfo(
                code='sw',
                name='Swahili',
                native_name='Kiswahili',
                region='National',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/swahili-kenya/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'  # Fallback
                ],
                tts_code='sw-KE'
            ),
            'ki': LanguageInfo(
                code='ki',
                name='Kikuyu',
                native_name='Gĩkũyũ',
                region='Central Kenya',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/kikuyu-fm/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'
                ],
                tts_code='sw-KE'  # Fallback to Swahili TTS
            ),
            'luo': LanguageInfo(
                code='luo',
                name='Luo',
                native_name='Dholuo',
                region='Nyanza',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/luo-fm/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'
                ],
                tts_code='sw-KE'
            ),
            'luy': LanguageInfo(
                code='luy',
                name='Luhya',
                native_name='Luluhya',
                region='Western Kenya',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/luhya-fm/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'
                ],
                tts_code='sw-KE'
            ),
            'kam': LanguageInfo(
                code='kam',
                name='Kamba',
                native_name='Kikamba',
                region='Eastern Kenya',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/kamba-fm/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'
                ],
                tts_code='sw-KE'
            ),
            'kal': LanguageInfo(
                code='kal',
                name='Kalenjin',
                native_name='Kalenjin',
                region='Rift Valley',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/kalenjin-fm/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'
                ],
                tts_code='sw-KE'
            )
        }
        
        # Define location-to-language mappings for Kenyan counties
        self.location_mappings = [
            # Central Kenya - Kikuyu dominant
            LocationLanguageMapping('Nairobi', 'en', ['sw', 'ki'], (-1.2921, 36.8219), 50),
            LocationLanguageMapping('Kiambu', 'ki', ['en', 'sw'], (-1.1719, 36.8356), 40),
            LocationLanguageMapping('Murang\'a', 'ki', ['en', 'sw'], (-0.7210, 37.1526), 35),
            LocationLanguageMapping('Nyeri', 'ki', ['en', 'sw'], (-0.4209, 36.9470), 35),
            LocationLanguageMapping('Kirinyaga', 'ki', ['en', 'sw'], (-0.6669, 37.3061), 30),
            LocationLanguageMapping('Nyandarua', 'ki', ['en', 'sw'], (-0.3048, 36.4442), 40),
            
            # Nyanza - Luo dominant  
            LocationLanguageMapping('Kisumu', 'luo', ['sw', 'en'], (-0.0917, 34.7680), 45),
            LocationLanguageMapping('Siaya', 'luo', ['sw', 'en'], (0.0607, 34.2738), 35),
            LocationLanguageMapping('Kisii', 'luo', ['sw', 'en'], (-0.6776, 34.7739), 30),
            LocationLanguageMapping('Nyamira', 'luo', ['sw', 'en'], (-0.5633, 34.9358), 25),
            LocationLanguageMapping('Homa Bay', 'luo', ['sw', 'en'], (-0.5273, 34.4571), 35),
            LocationLanguageMapping('Migori', 'luo', ['sw', 'en'], (-1.0634, 34.4734), 35),
            
            # Western Kenya - Luhya dominant
            LocationLanguageMapping('Kakamega', 'luy', ['sw', 'en'], (0.2827, 34.7519), 40),
            LocationLanguageMapping('Bungoma', 'luy', ['sw', 'en'], (0.5635, 34.5606), 35),
            LocationLanguageMapping('Busia', 'luy', ['sw', 'en'], (0.4601, 34.1112), 30),
            LocationLanguageMapping('Vihiga', 'luy', ['sw', 'en'], (0.0813, 34.7278), 25),
            
            # Eastern Kenya - Kamba dominant
            LocationLanguageMapping('Machakos', 'kam', ['sw', 'en'], (-1.5177, 37.2634), 40),
            LocationLanguageMapping('Kitui', 'kam', ['sw', 'en'], (-1.3667, 38.0109), 45),
            LocationLanguageMapping('Makueni', 'kam', ['sw', 'en'], (-1.8044, 37.6244), 35),
            
            # Rift Valley - Mixed, Kalenjin dominant in highlands
            LocationLanguageMapping('Nakuru', 'kal', ['sw', 'en'], (-0.3031, 36.0800), 50),
            LocationLanguageMapping('Eldoret', 'kal', ['sw', 'en'], (0.5143, 35.2697), 40),
            LocationLanguageMapping('Kericho', 'kal', ['sw', 'en'], (-0.3691, 35.2861), 35),
            LocationLanguageMapping('Nandi', 'kal', ['sw', 'en'], (0.1839, 35.1011), 30),
            LocationLanguageMapping('Uasin Gishu', 'kal', ['sw', 'en'], (0.5143, 35.2697), 35),
            
            # Coastal Region - Swahili dominant
            LocationLanguageMapping('Mombasa', 'sw', ['en'], (-4.0435, 39.6682), 30),
            LocationLanguageMapping('Kilifi', 'sw', ['en'], (-3.5051, 39.8498), 40),
            LocationLanguageMapping('Kwale', 'sw', ['en'], (-4.1733, 39.4512), 35),
            LocationLanguageMapping('Lamu', 'sw', ['en'], (-2.2717, 40.9020), 25),
            LocationLanguageMapping('Tana River', 'sw', ['en'], (-1.0131, 40.1315), 60),
            
            # Northern Kenya - Swahili/English
            LocationLanguageMapping('Garissa', 'sw', ['en'], (-0.4569, 39.6496), 80),
            LocationLanguageMapping('Wajir', 'sw', ['en'], (1.7471, 40.0573), 100),
            LocationLanguageMapping('Mandera', 'sw', ['en'], (3.9366, 41.8669), 80),
            LocationLanguageMapping('Marsabit', 'sw', ['en'], (2.3284, 37.9899), 120),
            LocationLanguageMapping('Isiolo', 'sw', ['en'], (0.3496, 37.5827), 60),
        ]

    def detect_language_from_coordinates(self, latitude: float, longitude: float) -> Dict[str, any]:
        """Detect the most appropriate language based on GPS coordinates"""
        cache_key = f"lang_detect_{latitude:.3f}_{longitude:.3f}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            best_match = None
            min_distance = float('inf')
            
            for mapping in self.location_mappings:
                # Calculate distance from point to mapping center
                distance = self._calculate_distance(
                    latitude, longitude,
                    mapping.coordinates[0], mapping.coordinates[1]
                )
                
                # Check if within radius and closer than previous matches
                if distance <= mapping.radius_km and distance < min_distance:
                    min_distance = distance
                    best_match = mapping

            if best_match:
                result = {
                    'detected_language': best_match.primary_language,
                    'alternative_languages': best_match.secondary_languages,
                    'county': best_match.county,
                    'distance_km': min_distance,
                    'confidence': max(0, 1 - (min_distance / best_match.radius_km)),
                    'language_info': self.languages.get(best_match.primary_language),
                    'radio_streams': self.languages.get(best_match.primary_language).radio_streams if best_match.primary_language in self.languages else []
                }
            else:
                # Default to English/Swahili if no match found
                result = {
                    'detected_language': 'en',
                    'alternative_languages': ['sw'],
                    'county': 'Unknown',
                    'distance_km': 0,
                    'confidence': 0.5,
                    'language_info': self.languages['en'],
                    'radio_streams': self.languages['en'].radio_streams
                }
            
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Error detecting language from coordinates: {e}")
            return {
                'detected_language': 'en',
                'alternative_languages': ['sw'],
                'county': 'Unknown',
                'distance_km': 0,
                'confidence': 0.5,
                'language_info': self.languages['en'],
                'radio_streams': self.languages['en'].radio_streams
            }

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        import math
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Earth's radius in kilometers
        
        return c * r

    def get_language_specific_content(self, language_code: str, content_type: str = 'general') -> Dict[str, any]:
        """Get content tailored to specific language/region"""
        if language_code not in self.languages:
            language_code = 'en'  # Default fallback
            
        language_info = self.languages[language_code]
        
        # Localized content templates
        content_templates = {
            'en': {
                'greeting': 'Welcome to Kagema FM',
                'weather_intro': 'Current weather in your area:',
                'news_intro': 'Here are the latest news updates:',
                'music_intro': 'Trending music for you:',
                'traffic_intro': 'Traffic update:',
                'emergency_prefix': 'EMERGENCY ALERT:'
            },
            'sw': {
                'greeting': 'Karibu Kagema FM',
                'weather_intro': 'Hali ya hewa eneo lako:',
                'news_intro': 'Hizi ndizo habari za hivi karibuni:',
                'music_intro': 'Muziki unaoongoza:',
                'traffic_intro': 'Taarifa za barabara:',
                'emergency_prefix': 'TAHADHARI:'
            },
            'ki': {
                'greeting': 'Wega Kagema FM',
                'weather_intro': 'Kĩrĩa kĩa rũũa eneo-inĩ:',
                'news_intro': 'Maya ma ũhoro wa rĩu:',
                'music_intro': 'Nyĩmbo iria irĩ mbere:',
                'traffic_intro': 'Ũhoro wa njĩra:',
                'emergency_prefix': 'TAHADHARI YA IHENYA:'
            },
            'luo': {
                'greeting': 'Oyawore e Kagema FM',
                'weather_intro': 'Kaka yamo e gwengʼu:',
                'news_intro': 'Wechegi mag sani:',
                'music_intro': 'Wende ma loko:',
                'traffic_intro': 'Weche mag yore:',
                'emergency_prefix': 'KIHONDKO MAPIYO:'
            },
            'luy': {
                'greeting': 'Mulakaye Kagema FM',
                'weather_intro': 'Esimba sia omulembe kwanu:',
                'news_intro': 'Amasale ka lelo:',
                'music_intro': 'Eshimba shiendi mulala:',
                'traffic_intro': 'Amasale ka tsinjira:',
                'emergency_prefix': 'OBULALI BUYSIA:'
            },
            'kam': {
                'greeting': 'Muliakaye Kagema FM',
                'weather_intro': 'Kĩlĩma kya ũvoo wanyu:',
                'news_intro': 'Makĩa ma ũmũnthĩ:',
                'music_intro': 'Nyĩmbo ila syũmaa:',
                'traffic_intro': 'Makĩa ma nzĩa:',
                'emergency_prefix': 'TAHADHARI YA HARAKA:'
            },
            'kal': {
                'greeting': 'Chamuge Kagema FM', 
                'weather_intro': 'Kerenget ne tilil agenge:',
                'news_intro': 'Tugul che kiit raini:',
                'music_intro': 'Muren che kitobei:',
                'traffic_intro': 'Tugul che ortinwek:',
                'emergency_prefix': 'KORETE NE CHAMYEI:'
            }
        }
        
        return {
            'language_info': language_info,
            'content': content_templates.get(language_code, content_templates['en']),
            'radio_streams': language_info.radio_streams,
            'tts_code': language_info.tts_code
        }

    def get_all_supported_languages(self) -> Dict[str, LanguageInfo]:
        """Get all supported languages"""
        return self.languages

    def get_regional_radio_stations(self, language_code: str) -> List[Dict[str, str]]:
        """Get radio stations for specific language/region"""
        if language_code not in self.languages:
            language_code = 'en'
            
        language_info = self.languages[language_code]
        
        # Mock regional stations data
        regional_stations = {
            'en': [
                {'name': 'Capital FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '98.4 FM'},
                {'name': 'Kiss FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '100.3 FM'},
                {'name': 'Classic 105', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '105.2 FM'}
            ],
            'sw': [
                {'name': 'Radio Citizen', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '106.7 FM'},
                {'name': 'Idhaa ya Kiswahili', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '95.6 FM'},
                {'name': 'Mbaitu FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '92.5 FM'}
            ],
            'ki': [
                {'name': 'Kameme FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '101.1 FM'},
                {'name': 'Inooro FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '98.9 FM'},
                {'name': 'Gukena FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '105.6 FM'}
            ],
            'luo': [
                {'name': 'Lake Victoria FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '94.4 FM'},
                {'name': 'Ramogi FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '107.1 FM'},
                {'name': 'Radio Nam Lolwe', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '96.7 FM'}
            ],
            'luy': [
                {'name': 'Musyi FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '102.8 FM'},
                {'name': 'West FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '94.9 FM'},
                {'name': 'Buluga FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '96.2 FM'}
            ],
            'kam': [
                {'name': 'Mbaitu FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '92.5 FM'},
                {'name': 'Syokimau FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '97.6 FM'},
                {'name': 'Athiani FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '104.3 FM'}
            ],
            'kal': [
                {'name': 'Kass FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '89.1 FM'},
                {'name': 'Chamge FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '92.7 FM'},
                {'name': 'Kipsang FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '95.9 FM'}
            ]
        }
        
        return regional_stations.get(language_code, regional_stations['en'])