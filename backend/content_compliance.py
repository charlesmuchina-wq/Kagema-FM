from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ContentRating(Enum):
    GENERAL = "general"           # All ages appropriate
    PARENTAL_GUIDANCE = "pg"      # Parental guidance suggested  
    MATURE = "mature"             # 16+ recommended
    ADULT = "adult"               # 18+ only
    EXPLICIT = "explicit"         # Contains explicit content

class ComplianceLevel(Enum):
    STRICT = "strict"             # Very conservative content filtering
    MODERATE = "moderate"         # Balanced content filtering  
    PERMISSIVE = "permissive"     # Minimal content filtering
    LOCAL_STANDARDS = "local"     # Defer to local regulations

@dataclass
class ContentDisclaimer:
    disclaimer_id: str
    title: str
    content: str
    applies_to: List[str]  # Content types this applies to
    severity: str          # warning, notice, critical
    language_code: str
    country_code: str
    last_updated: datetime

@dataclass
class RegionalCompliance:
    country: str
    region: Optional[str]
    content_rating_system: str
    adult_age_threshold: int
    explicit_content_allowed: bool
    government_regulations: List[str]
    content_warnings_required: bool
    broadcast_hours_restrictions: Optional[Dict[str, str]]

class ContentComplianceManager:
    def __init__(self):
        self.regional_compliance = self._load_regional_compliance()
        self.content_disclaimers = self._load_content_disclaimers()
        self.content_filters = {}
        
    def _load_regional_compliance(self) -> Dict[str, RegionalCompliance]:
        """Load regional compliance requirements for different countries"""
        return {
            # Kenya Compliance
            "KE": RegionalCompliance(
                country="Kenya",
                region=None,
                content_rating_system="Kenya Film Classification Board",
                adult_age_threshold=18,
                explicit_content_allowed=True,
                government_regulations=[
                    "Kenya Information and Communications Act",
                    "Kenya Film Classification Board Guidelines",
                    "Broadcasting Content Guidelines 2021"
                ],
                content_warnings_required=True,
                broadcast_hours_restrictions={
                    "adult_content": "21:00-05:00",
                    "explicit_language": "20:00-06:00"
                }
            ),
            
            # Brazil Compliance  
            "BR": RegionalCompliance(
                country="Brazil",
                region=None,
                content_rating_system="Classificação Indicativa",
                adult_age_threshold=18,
                explicit_content_allowed=True,
                government_regulations=[
                    "Lei Federal 8.069/90 (Estatuto da Criança e do Adolescente)",
                    "Portaria 1.220/2007 - Classificação Indicativa",
                    "Código Brasileiro de Telecomunicações"
                ],
                content_warnings_required=True,
                broadcast_hours_restrictions={
                    "adult_content": "23:00-06:00", 
                    "explicit_language": "20:00-06:00"
                }
            ),
            
            # United States Compliance
            "US": RegionalCompliance(
                country="United States",
                region=None,
                content_rating_system="FCC Content Guidelines",
                adult_age_threshold=18,
                explicit_content_allowed=True,
                government_regulations=[
                    "Communications Act of 1934",
                    "FCC Indecency and Profanity Rules",
                    "Children's Television Act"
                ],
                content_warnings_required=True,
                broadcast_hours_restrictions={
                    "indecent_content": "22:00-06:00"
                }
            ),
            
            # European Union General
            "EU": RegionalCompliance(
                country="European Union",
                region=None,
                content_rating_system="Audiovisual Media Services Directive",
                adult_age_threshold=18,
                explicit_content_allowed=True,
                government_regulations=[
                    "Audiovisual Media Services Directive (AVMSD)",
                    "General Data Protection Regulation (GDPR)",
                    "Digital Services Act"
                ],
                content_warnings_required=True,
                broadcast_hours_restrictions={
                    "adult_content": "22:00-06:00"
                }
            ),
            
            # Global Default Compliance
            "GLOBAL": RegionalCompliance(
                country="Global",
                region=None,
                content_rating_system="General Content Guidelines",
                adult_age_threshold=18,
                explicit_content_allowed=True,
                government_regulations=[
                    "Platform Terms of Service",
                    "Community Guidelines"
                ],
                content_warnings_required=True,
                broadcast_hours_restrictions={
                    "adult_content": "22:00-06:00",
                    "explicit_language": "20:00-06:00"
                }
            )
        }
    
    def _load_content_disclaimers(self) -> Dict[str, List[ContentDisclaimer]]:
        """Load content disclaimers for different languages and regions"""
        disclaimers = {}
        
        # English Disclaimers
        disclaimers["en"] = [
            ContentDisclaimer(
                disclaimer_id="platform_responsibility",
                title="Platform and Licensing Responsibility Notice",
                content="""IMPORTANT DISCLAIMER: Kagema FM is a radio integration platform and aggregator service only. We do not own, operate, or broadcast any radio content.

RADIO STATION RESPONSIBILITY: Each individual radio station accessed through this platform holds their own broadcasting licenses, content compliance responsibilities, and regulatory obligations. Radio stations are solely responsible for:
• Maintaining proper broadcasting licenses and permits
• Ensuring content compliance with local, regional, and national regulations
• Adhering to age-appropriate content guidelines and time restrictions
• Managing explicit content, language, and material standards
• Complying with all applicable government regulations and community standards

PLATFORM DISCLAIMER: Kagema FM serves only as a technical integration platform connecting users to third-party radio stations. We:
• Do not control, monitor, or approve radio station content
• Make no warranties regarding station licensing or regulatory compliance
• Assume no responsibility for content broadcast by individual stations
• Are not liable for station compliance failures or regulatory violations

USER RESPONSIBILITY: By using this service, you acknowledge that you are of legal age (18+) in your jurisdiction and understand that content compliance is the sole responsibility of individual radio stations, not the Kagema FM platform.""",
                applies_to=["radio_streams", "music", "news", "general_content"],
                severity="critical",
                language_code="en",
                country_code="GLOBAL",
                last_updated=datetime.now()
            ),
            ContentDisclaimer(
                disclaimer_id="explicit_content_warning",
                title="Explicit Content Warning", 
                content="""WARNING: This radio stream may contain explicit language, mature themes, and content intended for adult audiences only. Listener discretion is advised. Content may not be suitable for all audiences and may violate local community standards in some jurisdictions.

Parents and guardians are responsible for supervising minors' access to this content. Check your local regulations regarding explicit content broadcast times and accessibility.""",
                applies_to=["radio_streams", "music"],
                severity="warning",
                language_code="en",
                country_code="GLOBAL", 
                last_updated=datetime.now()
            ),
            ContentDisclaimer(
                disclaimer_id="kenya_compliance",
                title="Kenya Broadcasting Compliance",
                content="""Content broadcast through this platform must comply with Kenya Information and Communications Act and Kenya Film Classification Board Guidelines. Adult content may only be broadcast between 21:00 and 05:00 local time. 

Users broadcasting or accessing content in Kenya must ensure compliance with all applicable Kenyan broadcasting regulations and community standards.""",
                applies_to=["radio_streams", "news"],
                severity="notice",
                language_code="en",
                country_code="KE",
                last_updated=datetime.now()
            )
        ]
        
        # Portuguese (Brazilian) Disclaimers
        disclaimers["pt-br"] = [
            ContentDisclaimer(
                disclaimer_id="platform_responsibility",
                title="Aviso de Responsabilidade de Plataforma e Licenciamento",
                content="""AVISO IMPORTANTE: Kagema FM é apenas uma plataforma de integração e agregação de rádio. Não possuímos, operamos ou transmitimos qualquer conteúdo de rádio.

RESPONSABILIDADE DAS ESTAÇÕES DE RÁDIO: Cada estação de rádio individual acessada através desta plataforma possui suas próprias licenças de transmissão, responsabilidades de conformidade de conteúdo e obrigações regulamentares. As estações de rádio são as únicas responsáveis por:
• Manter licenças e autorizações de transmissão adequadas
• Garantir conformidade de conteúdo com regulamentações locais, regionais e nacionais
• Aderir às diretrizes de conteúdo apropriado para a idade e restrições de horário
• Gerenciar padrões de conteúdo explícito, linguagem e material
• Cumprir todos os regulamentos governamentais aplicáveis e padrões comunitários

ISENÇÃO DE RESPONSABILIDADE DA PLATAFORMA: Kagema FM serve apenas como plataforma técnica de integração conectando usuários a estações de rádio de terceiros. Nós:
• Não controlamos, monitoramos ou aprovamos o conteúdo das estações de rádio
• Não oferecemos garantias sobre licenciamento de estações ou conformidade regulamentar
• Não assumimos responsabilidade pelo conteúdo transmitido por estações individuais
• Não somos responsáveis por falhas de conformidade de estações ou violações regulamentares

RESPONSABILIDADE DO USUÁRIO: Ao usar este serviço, você reconhece que tem idade legal (18+) em sua jurisdição e entende que a conformidade de conteúdo é responsabilidade exclusiva das estações de rádio individuais, não da plataforma Kagema FM.""",
                applies_to=["radio_streams", "music", "news", "general_content"],
                severity="critical",
                language_code="pt-br",
                country_code="BR",
                last_updated=datetime.now()
            ),
            ContentDisclaimer(
                disclaimer_id="explicit_content_warning",
                title="Aviso de Conteúdo Explícito",
                content="""AVISO: Esta transmissão de rádio pode conter linguagem explícita, temas maduros e conteúdo destinado apenas a audiências adultas. Recomenda-se discrição do ouvinte. O conteúdo pode não ser adequado para todas as audiências e pode violar padrões comunitários locais em algumas jurisdições.

Pais e responsáveis são responsáveis por supervisionar o acesso de menores a este conteúdo. Verifique suas regulamentações locais sobre horários de transmissão de conteúdo explícito e acessibilidade.""",
                applies_to=["radio_streams", "music"],
                severity="warning",
                language_code="pt-br",
                country_code="BR",
                last_updated=datetime.now()
            ),
            ContentDisclaimer(
                disclaimer_id="brazil_compliance",
                title="Conformidade com Radiodifusão Brasileira",
                content="""O conteúdo transmitido através desta plataforma deve estar em conformidade com a Lei Federal 8.069/90 (Estatuto da Criança e do Adolescente) e Portaria 1.220/2007 - Classificação Indicativa. Conteúdo adulto só pode ser transmitido entre 23:00 e 06:00 horário local.

Usuários transmitindo ou acessando conteúdo no Brasil devem garantir conformidade com todas as regulamentações de radiodifusão brasileiras aplicáveis e padrões comunitários.""",
                applies_to=["radio_streams", "news"],
                severity="notice", 
                language_code="pt-br",
                country_code="BR",
                last_updated=datetime.now()
            )
        ]
        
        # Swahili Disclaimers
        disclaimers["sw"] = [
            ContentDisclaimer(
                disclaimer_id="platform_responsibility",
                title="Ilani ya Jukumu la Jukwaa na Leseni",
                content="""ILANI MUHIMU: Kagema FM ni jukwaa la uunganishaji wa redio na huduma ya ukusanyaji tu. Hatumiliki, hatuendeshi, au hatutangazi maudhui yoyote ya redio.

JUKUMU LA VITUO VYA REDIO: Kila kituo cha redio kinachofikiwa kupitia jukwaa hili kina leseni zake za utangazaji, majukumu ya kufuata maudhui, na majukumu ya kisheria. Vituo vya redio ndivyo vyenye jukumu pekee la:
• Kudumisha leseni na vibali vya utangazaji vinavyofaa
• Kuhakikisha maudhui yanafuata sheria za mitaa, kanda, na kitaifa
• Kufuata miongozo ya maudhui inayofaa kwa umri na vikwazo vya muda
• Kusimamia viwango vya maudhui ya wazi, lugha, na nyenzo
• Kufuata sheria zote za serikali zinazotumika na viwango vya jumuiya

KUJIONDOA KWA JUKWAA: Kagema FM hutumika tu kama jukwaa la kiufundi la uunganishaji linalowaunganisha watumiaji na vituo vya redio vya wahusika wa tatu. Sisi:
• Hatudhibiti, hakufuatilia, au hakuidhinisha maudhui ya vituo vya redio
• Hatutoi dhamana kuhusu leseni za vituo au kufuata sheria
• Hatuchukui jukumu la maudhui yanayotangazwa na vituo vya kibinafsi
• Hatuwajibiki kwa kushindwa kwa vituo kufuata au ukiukaji wa sheria

JUKUMU LA MTUMIAJI: Kwa kutumia huduma hii, unakubali kuwa una umri halali (miaka 18+) katika mamlaka yako na unaelewa kuwa kufuata maudhui ni jukumu pekee la vituo vya redio vya kibinafsi, si jukwaa la Kagema FM.""",
                applies_to=["radio_streams", "music", "news", "general_content"],
                severity="critical",
                language_code="sw", 
                country_code="KE",
                last_updated=datetime.now()
            )
        ]
        
        return disclaimers
    
    def get_applicable_disclaimers(self, country_code: str, language_code: str, content_types: List[str]) -> List[ContentDisclaimer]:
        """Get all applicable disclaimers for given country, language, and content types"""
        applicable_disclaimers = []
        
        # Get language-specific disclaimers
        if language_code in self.content_disclaimers:
            for disclaimer in self.content_disclaimers[language_code]:
                # Check if disclaimer applies to country and content types
                if (disclaimer.country_code == country_code or disclaimer.country_code == "GLOBAL"):
                    if any(content_type in disclaimer.applies_to for content_type in content_types):
                        applicable_disclaimers.append(disclaimer)
        
        # Fallback to English if no language-specific disclaimers found
        if not applicable_disclaimers and "en" in self.content_disclaimers:
            for disclaimer in self.content_disclaimers["en"]:
                if (disclaimer.country_code == country_code or disclaimer.country_code == "GLOBAL"):
                    if any(content_type in disclaimer.applies_to for content_type in content_types):
                        applicable_disclaimers.append(disclaimer)
        
        return applicable_disclaimers
    
    def get_regional_compliance(self, country_code: str) -> Optional[RegionalCompliance]:
        """Get regional compliance requirements for a country"""
        return self.regional_compliance.get(country_code)
    
    def check_content_rating_compliance(self, content_rating: ContentRating, user_age: int, country_code: str, current_hour: int) -> Dict[str, Any]:
        """Check if content is compliant with regional regulations"""
        compliance = self.get_regional_compliance(country_code)
        if not compliance:
            compliance = self.regional_compliance.get("GLOBAL")
        
        # Fallback to default if still None
        if not compliance:
            compliance = RegionalCompliance(
                country="Default",
                region=None,
                content_rating_system="General Guidelines",
                adult_age_threshold=18,
                explicit_content_allowed=True,
                government_regulations=[],
                content_warnings_required=True,
                broadcast_hours_restrictions={}
            )
        
        result = {
            "compliant": True,
            "warnings": [],
            "blocking_reasons": [],
            "age_appropriate": True,
            "time_appropriate": True
        }
        
        # Check age compliance
        if content_rating in [ContentRating.ADULT, ContentRating.EXPLICIT]:
            if user_age < compliance.adult_age_threshold:
                result["compliant"] = False
                result["age_appropriate"] = False
                result["blocking_reasons"].append(f"Content rated {content_rating.value} requires minimum age {compliance.adult_age_threshold}")
        
        # Check time restrictions
        if compliance.broadcast_hours_restrictions:
            if content_rating == ContentRating.ADULT and "adult_content" in compliance.broadcast_hours_restrictions:
                restriction = compliance.broadcast_hours_restrictions["adult_content"]
                start_hour, end_hour = self._parse_time_restriction(restriction)
                if not self._is_time_allowed(current_hour, start_hour, end_hour):
                    result["compliant"] = False
                    result["time_appropriate"] = False
                    result["warnings"].append(f"Adult content only allowed during {restriction}")
            
            if content_rating == ContentRating.EXPLICIT and "explicit_language" in compliance.broadcast_hours_restrictions:
                restriction = compliance.broadcast_hours_restrictions["explicit_language"]
                start_hour, end_hour = self._parse_time_restriction(restriction)
                if not self._is_time_allowed(current_hour, start_hour, end_hour):
                    result["compliant"] = False
                    result["time_appropriate"] = False
                    result["warnings"].append(f"Explicit content only allowed during {restriction}")
        
        return result
    
    def _parse_time_restriction(self, restriction: str) -> tuple:
        """Parse time restriction string like '21:00-05:00' into hour integers"""
        try:
            start_time, end_time = restriction.split('-')
            start_hour = int(start_time.split(':')[0])
            end_hour = int(end_time.split(':')[0])
            return start_hour, end_hour
        except Exception as e:
            print(f"Error in time restriction parsing: {e}")
            return 0, 23  # Default to no restrictions
    
    def _is_time_allowed(self, current_hour: int, start_hour: int, end_hour: int) -> bool:
        """Check if current time is within allowed broadcast hours"""
        if start_hour <= end_hour:
            # Same day range (e.g., 08:00-18:00)
            return start_hour <= current_hour <= end_hour
        else:
            # Overnight range (e.g., 21:00-05:00) 
            return current_hour >= start_hour or current_hour <= end_hour
    
    def generate_content_warning_response(self, country_code: str, language_code: str, content_types: List[str]) -> Dict[str, Any]:
        """Generate complete content warning response for API"""
        disclaimers = self.get_applicable_disclaimers(country_code, language_code, content_types)
        compliance = self.get_regional_compliance(country_code)
        
        return {
            "content_disclaimers": [
                {
                    "id": disclaimer.disclaimer_id,
                    "title": disclaimer.title,
                    "content": disclaimer.content,
                    "severity": disclaimer.severity,
                    "applies_to": disclaimer.applies_to
                } for disclaimer in disclaimers
            ],
            "regional_compliance": {
                "country": compliance.country if compliance else "Unknown",
                "content_rating_system": compliance.content_rating_system if compliance else "Generic",
                "adult_age_threshold": compliance.adult_age_threshold if compliance else 18,
                "content_warnings_required": compliance.content_warnings_required if compliance else True,
                "government_regulations": compliance.government_regulations if compliance else []
            },
            "user_acknowledgment_required": True,
            "compliance_version": "1.0",
            "last_updated": datetime.now().isoformat()
        }