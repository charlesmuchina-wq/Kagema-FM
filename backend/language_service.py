from typing import Dict, List, Tuple
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
        
        # Define supported languages in Kenya and Brazil
        self.languages = {
            # Kenyan Languages
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
            ),
            
            # Brazilian Portuguese
            'pt-br': LanguageInfo(
                code='pt-br',
                name='Portuguese (Brazil)',
                native_name='Português Brasileiro',
                region='Nacional',
                radio_streams=[
                    'http://ice1.somafm.com/groovesalad-256-mp3',  # Default stream
                    'https://radio.garden/api/ara/content/listen/brasil-fm/channel.mp3'
                ],
                tts_code='pt-BR'
            ),
            'pt-sp': LanguageInfo(
                code='pt-sp',
                name='Portuguese (São Paulo)',
                native_name='Português Paulista',
                region='Sudeste',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/sao-paulo-fm/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'
                ],
                tts_code='pt-BR'
            ),
            'pt-rj': LanguageInfo(
                code='pt-rj',
                name='Portuguese (Rio de Janeiro)',
                native_name='Português Carioca',
                region='Sudeste',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/rio-fm/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'
                ],
                tts_code='pt-BR'
            ),
            'pt-mg': LanguageInfo(
                code='pt-mg',
                name='Portuguese (Minas Gerais)',
                native_name='Português Mineiro',
                region='Sudeste',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/minas-fm/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'
                ],
                tts_code='pt-BR'
            ),
            'pt-rs': LanguageInfo(
                code='pt-rs',
                name='Portuguese (Rio Grande do Sul)',
                native_name='Português Gaúcho',
                region='Sul',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/gaucho-fm/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'
                ],
                tts_code='pt-BR'
            ),
            'pt-ba': LanguageInfo(
                code='pt-ba',
                name='Portuguese (Bahia)',
                native_name='Português Baiano',
                region='Nordeste',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/bahia-fm/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'
                ],
                tts_code='pt-BR'
            ),
            'pt-pe': LanguageInfo(
                code='pt-pe',
                name='Portuguese (Pernambuco)',
                native_name='Português Pernambucano',
                region='Nordeste',
                radio_streams=[
                    'https://radio.garden/api/ara/content/listen/pernambuco-fm/channel.mp3',
                    'http://ice1.somafm.com/groovesalad-256-mp3'
                ],
                tts_code='pt-BR'
            )
        }
        
        # Define location-to-language mappings for Kenya and Brazil
        self.location_mappings = [
            # KENYA - Central Kenya - Kikuyu dominant
            LocationLanguageMapping('Nairobi', 'en', ['sw', 'ki'], (-1.2921, 36.8219), 50),
            LocationLanguageMapping('Kiambu', 'ki', ['en', 'sw'], (-1.1719, 36.8356), 40),
            LocationLanguageMapping('Murang\'a', 'ki', ['en', 'sw'], (-0.7210, 37.1526), 35),
            LocationLanguageMapping('Nyeri', 'ki', ['en', 'sw'], (-0.4209, 36.9470), 35),
            LocationLanguageMapping('Kirinyaga', 'ki', ['en', 'sw'], (-0.6669, 37.3061), 30),
            LocationLanguageMapping('Nyandarua', 'ki', ['en', 'sw'], (-0.3048, 36.4442), 40),
            
            # KENYA - Nyanza - Luo dominant  
            LocationLanguageMapping('Kisumu', 'luo', ['sw', 'en'], (-0.0917, 34.7680), 45),
            LocationLanguageMapping('Siaya', 'luo', ['sw', 'en'], (0.0607, 34.2738), 35),
            LocationLanguageMapping('Kisii', 'luo', ['sw', 'en'], (-0.6776, 34.7739), 30),
            LocationLanguageMapping('Nyamira', 'luo', ['sw', 'en'], (-0.5633, 34.9358), 25),
            LocationLanguageMapping('Homa Bay', 'luo', ['sw', 'en'], (-0.5273, 34.4571), 35),
            LocationLanguageMapping('Migori', 'luo', ['sw', 'en'], (-1.0634, 34.4734), 35),
            
            # KENYA - Western Kenya - Luhya dominant
            LocationLanguageMapping('Kakamega', 'luy', ['sw', 'en'], (0.2827, 34.7519), 40),
            LocationLanguageMapping('Bungoma', 'luy', ['sw', 'en'], (0.5635, 34.5606), 35),
            LocationLanguageMapping('Busia', 'luy', ['sw', 'en'], (0.4601, 34.1112), 30),
            LocationLanguageMapping('Vihiga', 'luy', ['sw', 'en'], (0.0813, 34.7278), 25),
            
            # KENYA - Eastern Kenya - Kamba dominant
            LocationLanguageMapping('Machakos', 'kam', ['sw', 'en'], (-1.5177, 37.2634), 40),
            LocationLanguageMapping('Kitui', 'kam', ['sw', 'en'], (-1.3667, 38.0109), 45),
            LocationLanguageMapping('Makueni', 'kam', ['sw', 'en'], (-1.8044, 37.6244), 35),
            
            # KENYA - Rift Valley - Mixed, Kalenjin dominant in highlands
            LocationLanguageMapping('Nakuru', 'kal', ['sw', 'en'], (-0.3031, 36.0800), 50),
            LocationLanguageMapping('Eldoret', 'kal', ['sw', 'en'], (0.5143, 35.2697), 40),
            LocationLanguageMapping('Kericho', 'kal', ['sw', 'en'], (-0.3691, 35.2861), 35),
            LocationLanguageMapping('Nandi', 'kal', ['sw', 'en'], (0.1839, 35.1011), 30),
            LocationLanguageMapping('Uasin Gishu', 'kal', ['sw', 'en'], (0.5143, 35.2697), 35),
            
            # KENYA - Coastal Region - Swahili dominant
            LocationLanguageMapping('Mombasa', 'sw', ['en'], (-4.0435, 39.6682), 30),
            LocationLanguageMapping('Kilifi', 'sw', ['en'], (-3.5051, 39.8498), 40),
            LocationLanguageMapping('Kwale', 'sw', ['en'], (-4.1733, 39.4512), 35),
            LocationLanguageMapping('Lamu', 'sw', ['en'], (-2.2717, 40.9020), 25),
            LocationLanguageMapping('Tana River', 'sw', ['en'], (-1.0131, 40.1315), 60),
            
            # KENYA - Northern Kenya - Swahili/English
            LocationLanguageMapping('Garissa', 'sw', ['en'], (-0.4569, 39.6496), 80),
            LocationLanguageMapping('Wajir', 'sw', ['en'], (1.7471, 40.0573), 100),
            LocationLanguageMapping('Mandera', 'sw', ['en'], (3.9366, 41.8669), 80),
            LocationLanguageMapping('Marsabit', 'sw', ['en'], (2.3284, 37.9899), 120),
            LocationLanguageMapping('Isiolo', 'sw', ['en'], (0.3496, 37.5827), 60),
            
            # BRAZIL - Sudeste Region - São Paulo
            LocationLanguageMapping('São Paulo', 'pt-sp', ['pt-br'], (-23.5505, -46.6333), 80),
            LocationLanguageMapping('Campinas', 'pt-sp', ['pt-br'], (-22.9056, -47.0608), 40),
            LocationLanguageMapping('Santos', 'pt-sp', ['pt-br'], (-23.9608, -46.3334), 30),
            LocationLanguageMapping('São José dos Campos', 'pt-sp', ['pt-br'], (-23.1775, -45.8844), 35),
            LocationLanguageMapping('Ribeirão Preto', 'pt-sp', ['pt-br'], (-21.1775, -47.8103), 40),
            LocationLanguageMapping('Sorocaba', 'pt-sp', ['pt-br'], (-23.5015, -47.4526), 30),
            
            # BRAZIL - Rio de Janeiro
            LocationLanguageMapping('Rio de Janeiro', 'pt-rj', ['pt-br'], (-22.9068, -43.1729), 60),
            LocationLanguageMapping('Niterói', 'pt-rj', ['pt-br'], (-22.8833, -43.1036), 25),
            LocationLanguageMapping('Nova Iguaçu', 'pt-rj', ['pt-br'], (-22.7511, -43.4511), 30),
            LocationLanguageMapping('Duque de Caxias', 'pt-rj', ['pt-br'], (-22.7856, -43.3117), 25),
            LocationLanguageMapping('Cabo Frio', 'pt-rj', ['pt-br'], (-22.8794, -42.0175), 35),
            
            # BRAZIL - Minas Gerais
            LocationLanguageMapping('Belo Horizonte', 'pt-mg', ['pt-br'], (-19.9191, -43.9386), 70),
            LocationLanguageMapping('Uberlândia', 'pt-mg', ['pt-br'], (-18.9113, -48.2622), 40),
            LocationLanguageMapping('Contagem', 'pt-mg', ['pt-br'], (-19.9317, -44.0536), 25),
            LocationLanguageMapping('Juiz de Fora', 'pt-mg', ['pt-br'], (-21.7642, -43.3506), 35),
            LocationLanguageMapping('Betim', 'pt-mg', ['pt-br'], (-19.9678, -44.1975), 30),
            
            # BRAZIL - Sul Region - Rio Grande do Sul
            LocationLanguageMapping('Porto Alegre', 'pt-rs', ['pt-br'], (-30.0346, -51.2177), 60),
            LocationLanguageMapping('Caxias do Sul', 'pt-rs', ['pt-br'], (-29.1678, -51.1794), 35),
            LocationLanguageMapping('Pelotas', 'pt-rs', ['pt-br'], (-31.7654, -52.3376), 40),
            LocationLanguageMapping('Santa Maria', 'pt-rs', ['pt-br'], (-29.6842, -53.8069), 45),
            LocationLanguageMapping('Canoas', 'pt-rs', ['pt-br'], (-29.9175, -51.1844), 25),
            
            # BRAZIL - Paraná
            LocationLanguageMapping('Curitiba', 'pt-rs', ['pt-br'], (-25.4284, -49.2733), 60),
            LocationLanguageMapping('Londrina', 'pt-rs', ['pt-br'], (-23.3045, -51.1696), 40),
            LocationLanguageMapping('Maringá', 'pt-rs', ['pt-br'], (-23.4273, -51.9375), 35),
            LocationLanguageMapping('Ponta Grossa', 'pt-rs', ['pt-br'], (-25.0916, -50.1668), 30),
            
            # BRAZIL - Santa Catarina
            LocationLanguageMapping('Florianópolis', 'pt-rs', ['pt-br'], (-27.5954, -48.5480), 50),
            LocationLanguageMapping('Joinville', 'pt-rs', ['pt-br'], (-26.3044, -48.8487), 35),
            LocationLanguageMapping('Blumenau', 'pt-rs', ['pt-br'], (-26.9194, -49.0661), 30),
            LocationLanguageMapping('São José', 'pt-rs', ['pt-br'], (-27.6103, -48.6350), 25),
            
            # BRAZIL - Nordeste Region - Bahia (FIXED)
            LocationLanguageMapping('Salvador', 'pt-ba', ['pt-br'], (-12.9714, -38.5014), 70),
            LocationLanguageMapping('Feira de Santana', 'pt-ba', ['pt-br'], (-12.2664, -38.9663), 40),
            LocationLanguageMapping('Vitória da Conquista', 'pt-ba', ['pt-br'], (-14.8719, -40.8394), 45),
            LocationLanguageMapping('Camaçari', 'pt-ba', ['pt-br'], (-12.6975, -38.3242), 30),
            LocationLanguageMapping('Itabuna', 'pt-ba', ['pt-br'], (-14.7886, -39.2803), 35),
            LocationLanguageMapping('Lauro de Freitas', 'pt-ba', ['pt-br'], (-12.8944, -38.3275), 25),
            LocationLanguageMapping('Juazeiro', 'pt-ba', ['pt-br'], (-9.411, -40.4986), 40),
            LocationLanguageMapping('Alagoinhas', 'pt-ba', ['pt-br'], (-12.1353, -38.4197), 30),
            
            # BRAZIL - Pernambuco
            LocationLanguageMapping('Recife', 'pt-pe', ['pt-br'], (-8.0476, -34.8770), 60),
            LocationLanguageMapping('Jaboatão dos Guararapes', 'pt-pe', ['pt-br'], (-8.1128, -35.0144), 30),
            LocationLanguageMapping('Olinda', 'pt-pe', ['pt-br'], (-8.0089, -34.8553), 25),
            LocationLanguageMapping('Caruaru', 'pt-pe', ['pt-br'], (-8.2836, -35.9761), 40),
            LocationLanguageMapping('Petrolina', 'pt-pe', ['pt-br'], (-9.3891, -40.5006), 45),
            
            # BRAZIL - Ceará
            LocationLanguageMapping('Fortaleza', 'pt-pe', ['pt-br'], (-3.7172, -38.5434), 80),
            LocationLanguageMapping('Caucaia', 'pt-pe', ['pt-br'], (-3.7327, -38.6531), 30),
            LocationLanguageMapping('Juazeiro do Norte', 'pt-pe', ['pt-br'], (-7.2128, -39.3153), 40),
            LocationLanguageMapping('Maracanaú', 'pt-pe', ['pt-br'], (-3.8756, -38.6253), 25),
            
            # BRAZIL - Centro-Oeste - Brasília
            LocationLanguageMapping('Brasília', 'pt-br', ['pt-sp'], (-15.7942, -47.8822), 100),
            LocationLanguageMapping('Goiânia', 'pt-br', ['pt-sp'], (-16.6869, -49.2648), 60),
            LocationLanguageMapping('Campo Grande', 'pt-br', ['pt-sp'], (-20.4697, -54.6201), 80),
            LocationLanguageMapping('Cuiabá', 'pt-br', ['pt-sp'], (-15.6014, -56.0979), 70),
            
            # BRAZIL - Norte Region
            LocationLanguageMapping('Manaus', 'pt-br', ['pt-pe'], (-3.1190, -60.0217), 120),
            LocationLanguageMapping('Belém', 'pt-br', ['pt-pe'], (-1.4558, -48.5044), 100),
            LocationLanguageMapping('Porto Velho', 'pt-br', ['pt-pe'], (-8.7612, -63.9023), 80),
            LocationLanguageMapping('Boa Vista', 'pt-br', ['pt-pe'], (2.8235, -60.6758), 90),
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
        
        # Localized content templates for Kenya and Brazil
        content_templates = {
            # Kenyan Languages
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
            },
            
            # Brazilian Portuguese Variants
            'pt-br': {
                'greeting': 'Bem-vindos à Kagema FM',
                'weather_intro': 'Clima atual na sua região:',
                'news_intro': 'Aqui estão as últimas notícias:',
                'music_intro': 'Música em alta para você:',
                'traffic_intro': 'Informação do trânsito:',
                'emergency_prefix': 'ALERTA DE EMERGÊNCIA:'
            },
            'pt-sp': {
                'greeting': 'E aí, galera! Bem-vindos à Kagema FM',
                'weather_intro': 'O tempo aí na sua área:',
                'news_intro': 'Ó as notícias fresquinhas:',
                'music_intro': 'Os hits que tão bombando:',
                'traffic_intro': 'Como tá o trânsito por aí:',
                'emergency_prefix': 'ATENÇÃO! EMERGÊNCIA:'
            },
            'pt-rj': {
                'greeting': 'Opa! Salve, salve! Kagema FM na área',
                'weather_intro': 'O tempo aqui no Rio:',
                'news_intro': 'As notícias que tão rolando:',
                'music_intro': 'O som que tá pegando:',
                'traffic_intro': 'Como tá o trânsito na cidade:',
                'emergency_prefix': 'ATENÇÃO GERAL:'
            },
            'pt-mg': {
                'greeting': 'Ô sô! Bem-vindos à Kagema FM',
                'weather_intro': 'O tempo aqui em Minas:',
                'news_intro': 'As notícias de hoje:',
                'music_intro': 'A música boa de sempre:',
                'traffic_intro': 'Situação do trânsito:',
                'emergency_prefix': 'ATENÇÃO! EMERGÊNCIA:'
            },
            'pt-rs': {
                'greeting': 'Bah, tchê! Kagema FM no ar',
                'weather_intro': 'O tempo aqui no Sul:',
                'news_intro': 'As notícias do dia:',
                'music_intro': 'A música que tá tocando:',
                'traffic_intro': 'Como anda o trânsito:',
                'emergency_prefix': 'ATENÇÃO TCHÊ!'
            },
            'pt-ba': {
                'greeting': 'Ô meu rei! Kagema FM na Bahia',
                'weather_intro': 'O tempo aqui na Bahia:',
                'news_intro': 'As notícias de hoje:',
                'music_intro': 'O axé e o som que rola:',
                'traffic_intro': 'Trânsito na cidade:',
                'emergency_prefix': 'ATENÇÃO PESSOAL:'
            },
            'pt-pe': {
                'greeting': 'Ô cabra! Kagema FM no Nordeste',
                'weather_intro': 'O tempo aqui no Nordeste:',
                'news_intro': 'As notícias da região:',
                'music_intro': 'O forró e os sucessos:',
                'traffic_intro': 'Situação do trânsito:',
                'emergency_prefix': 'ATENÇÃO PESSOAL:'
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
        
        # Mock regional stations data for Kenya and Brazil
        regional_stations = {
            # Kenyan Stations
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
            ],
            
            # Brazilian Stations
            'pt-br': [
                {'name': 'CBN Brasil', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '90.5 FM'},
                {'name': 'Jovem Pan FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '100.9 FM'},
                {'name': 'Kiss FM Brasil', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '102.1 FM'}
            ],
            'pt-sp': [
                {'name': 'Radio Eldorado', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '107.3 FM'},
                {'name': 'Mix FM São Paulo', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '106.3 FM'},
                {'name': 'Alpha FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '101.7 FM'}
            ],
            'pt-rj': [
                {'name': 'Radio Tupi', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '96.5 FM'},
                {'name': 'Kiss FM Rio', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '102.1 FM'},
                {'name': 'Radio Globo', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '98.1 FM'}
            ],
            'pt-mg': [
                {'name': 'Radio Itatiaia', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '95.7 FM'},
                {'name': 'Radio Inconfidência', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '100.9 FM'},
                {'name': 'Mix FM BH', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '102.1 FM'}
            ],
            'pt-rs': [
                {'name': 'Radio Gaúcha', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '93.7 FM'},
                {'name': 'Atlântida FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '100.9 FM'},
                {'name': 'Radio Farroupilha', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '680 AM'}
            ],
            'pt-ba': [
                {'name': 'Radio Metrópole', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '101.1 FM'},
                {'name': 'Massa FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '96.9 FM'},
                {'name': 'Itapoan FM', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '94.7 FM'}
            ],
            'pt-pe': [
                {'name': 'Radio Jornal', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '100.7 FM'},
                {'name': 'Rádio Clube', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '99.1 FM'},
                {'name': 'Mix FM Recife', 'stream': 'http://ice1.somafm.com/groovesalad-256-mp3', 'frequency': '107.9 FM'}
            ]
        }
        
        return regional_stations.get(language_code, regional_stations['en'])