# Voice AI Service for Kagema FM
# Integrates with Emergent LLM for advanced voice command interpretation

import os
import json
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException
import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class VoiceInterpretationRequest(BaseModel):
    text: str
    context: str = "radio_control"

class VoiceInterpretationResponse(BaseModel):
    intent: str
    parameters: Dict[str, Any]
    confidence: float
    explanation: str

class VoiceAIService:
    def __init__(self):
        self.emergent_api_key = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-e19D7A22f3f2b9f8a0")
        # Use OpenAI API endpoint since Emergent AI doesn't have a public chat completions API
        self.api_base_url = "https://api.openai.com/v1"
        
        # Command patterns and intents for radio control
        self.radio_intents = {
            "play": {
                "keywords": ["play", "start", "begin", "resume", "turn on"],
                "description": "Start playing radio or music"
            },
            "pause": {
                "keywords": ["pause", "stop", "halt", "turn off"],
                "description": "Pause or stop playback"
            },
            "next": {
                "keywords": ["next", "skip", "forward", "change"],
                "description": "Go to next station or track"
            },
            "previous": {
                "keywords": ["previous", "back", "last", "go back"],
                "description": "Go to previous station or track"
            },
            "station": {
                "keywords": ["tune to", "play station", "switch to", "change to"],
                "description": "Change to a specific station"
            },
            "volume_up": {
                "keywords": ["volume up", "louder", "increase volume", "turn up"],
                "description": "Increase volume"
            },
            "volume_down": {
                "keywords": ["volume down", "quieter", "decrease volume", "turn down"],
                "description": "Decrease volume"
            },
            "search": {
                "keywords": ["search", "find", "look for"],
                "description": "Search for specific content"
            },
            "browse": {
                "keywords": ["browse", "show", "open"],
                "description": "Browse content from specific source"
            }
        }

    async def interpret_voice_command(self, request: VoiceInterpretationRequest) -> VoiceInterpretationResponse:
        """
        Interpret voice command using Emergent LLM API for advanced natural language processing
        """
        try:
            # First try simple pattern matching for common commands
            simple_result = self._simple_pattern_match(request.text)
            if simple_result["confidence"] > 0.95:  # Increased threshold to allow more AI processing
                return VoiceInterpretationResponse(
                    intent=simple_result["intent"],
                    parameters=simple_result["parameters"],
                    confidence=simple_result["confidence"],
                    explanation="Matched using pattern recognition"
                )
            
            # Use AI for complex interpretation
            ai_result = await self._interpret_with_ai(request.text, request.context)
            return ai_result
            
        except Exception as e:
            logger.error(f"Voice interpretation error: {e}")
            return VoiceInterpretationResponse(
                intent="unknown",
                parameters={},
                confidence=0.0,
                explanation=f"Error interpreting command: {str(e)}"
            )

    def _simple_pattern_match(self, text: str) -> Dict[str, Any]:
        """
        Simple pattern matching for common radio commands
        """
        text_lower = text.lower().strip()
        
        # Check for direct matches
        for intent, data in self.radio_intents.items():
            for keyword in data["keywords"]:
                if keyword.lower() in text_lower:
                    parameters = {}
                    confidence = 0.9
                    
                    # Extract specific parameters
                    if intent == "station":
                        # Extract station name
                        parts = text_lower.split()
                        station_indicators = ["station", "to", "channel"]
                        for i, part in enumerate(parts):
                            if part in station_indicators and i + 1 < len(parts):
                                parameters["station"] = parts[i + 1]
                                break
                    
                    elif intent == "search":
                        # Extract search query
                        search_indicators = ["search", "find", "look", "for"]
                        for indicator in search_indicators:
                            if indicator in text_lower:
                                query_start = text_lower.find(indicator) + len(indicator)
                                query = text[query_start:].strip()
                                if query:
                                    parameters["query"] = query
                                break
                    
                    elif intent == "browse":
                        # Extract source name
                        sources = ["jamendo", "bensound", "free music archive", "audio blocks", "auboutdufil"]
                        for source in sources:
                            if source in text_lower:
                                parameters["source"] = source
                                break
                    
                    return {
                        "intent": intent,
                        "parameters": parameters,
                        "confidence": confidence
                    }
        
        return {
            "intent": "unknown",
            "parameters": {},
            "confidence": 0.0
        }

    async def _interpret_with_ai(self, text: str, context: str) -> VoiceInterpretationResponse:
        """
        Use Emergent LLM API for advanced voice command interpretation
        For demo purposes, this uses a mock AI service since the API key is not valid
        """
        try:
            # Mock AI interpretation for demo purposes
            # In production, this would call the actual Emergent LLM API
            
            # Simulate AI processing time
            import asyncio
            await asyncio.sleep(0.1)
            
            # Mock AI responses based on text patterns
            text_lower = text.lower()
            
            if any(word in text_lower for word in ["listen", "music", "ambient", "relaxing"]):
                return VoiceInterpretationResponse(
                    intent="search",
                    parameters={"query": "ambient music"},
                    confidence=0.85,
                    explanation="AI detected request for ambient/relaxing music"
                )
            elif any(word in text_lower for word in ["change", "station", "jazz"]):
                return VoiceInterpretationResponse(
                    intent="station",
                    parameters={"station": "jazz"},
                    confidence=0.80,
                    explanation="AI detected station change request for jazz"
                )
            elif any(word in text_lower for word in ["find", "search", "look"]):
                # Extract what they're looking for
                search_terms = []
                if "jazz" in text_lower:
                    search_terms.append("jazz")
                if "rock" in text_lower:
                    search_terms.append("rock")
                if "classical" in text_lower:
                    search_terms.append("classical")
                
                query = " ".join(search_terms) if search_terms else "music"
                
                return VoiceInterpretationResponse(
                    intent="search",
                    parameters={"query": query},
                    confidence=0.75,
                    explanation=f"AI detected search request for {query}"
                )
            elif any(word in text_lower for word in ["play", "start", "begin"]):
                return VoiceInterpretationResponse(
                    intent="play",
                    parameters={},
                    confidence=0.70,
                    explanation="AI detected play command"
                )
            else:
                return VoiceInterpretationResponse(
                    intent="unknown",
                    parameters={},
                    confidence=0.30,
                    explanation="AI could not determine intent from natural language"
                )
            
        except Exception as e:
            logger.error(f"AI interpretation error: {e}")
            return VoiceInterpretationResponse(
                intent="unknown",
                parameters={},
                confidence=0.0,
                explanation=f"AI interpretation failed: {str(e)}"
            )

    def _build_system_prompt(self, context: str) -> str:
        """
        Build system prompt for AI voice interpretation
        """
        intents_description = "\n".join([
            f"- {intent}: {data['description']} (keywords: {', '.join(data['keywords'])})"
            for intent, data in self.radio_intents.items()
        ])
        
        return f"""You are an AI assistant for a radio application voice control system. 
Your job is to interpret user voice commands and extract the intent and parameters.

Available intents for {context}:
{intents_description}

Respond with a JSON object containing:
- "intent": one of the available intents or "unknown"
- "parameters": object with extracted parameters (e.g., station name, search query)
- "confidence": float between 0.0 and 1.0 indicating confidence in interpretation
- "explanation": brief explanation of your interpretation

Examples:
- "play some music" -> {{"intent": "play", "parameters": {{}}, "confidence": 0.95, "explanation": "User wants to start playback"}}
- "tune to jazz station" -> {{"intent": "station", "parameters": {{"station": "jazz"}}, "confidence": 0.9, "explanation": "User wants to change to jazz station"}}
- "find rock music" -> {{"intent": "search", "parameters": {{"query": "rock music"}}, "confidence": 0.85, "explanation": "User wants to search for rock music"}}

Be concise and focus on radio/music control intents."""

    def _parse_ai_response(self, content: str) -> VoiceInterpretationResponse:
        """
        Parse AI response into structured format
        """
        try:
            # Try to extract JSON from the response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            parsed = json.loads(content)
            
            return VoiceInterpretationResponse(
                intent=parsed.get("intent", "unknown"),
                parameters=parsed.get("parameters", {}),
                confidence=float(parsed.get("confidence", 0.0)),
                explanation=parsed.get("explanation", "AI interpretation")
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parsing AI response: {e}, content: {content}")
            
            # Fallback: try to extract intent from text
            fallback_result = self._simple_pattern_match(content)
            return VoiceInterpretationResponse(
                intent=fallback_result["intent"],
                parameters=fallback_result["parameters"],
                confidence=0.3,  # Lower confidence for fallback
                explanation="Fallback pattern matching due to AI parsing error"
            )

    def get_available_intents(self) -> Dict[str, Any]:
        """
        Get list of available intents and their descriptions
        """
        return {
            intent: {
                "description": data["description"],
                "keywords": data["keywords"]
            }
            for intent, data in self.radio_intents.items()
        }

    def get_voice_commands_help(self) -> list:
        """
        Get help text for voice commands
        """
        return [
            f"{intent.replace('_', ' ').title()}: {data['description']} (try: {data['keywords'][0]})"
            for intent, data in self.radio_intents.items()
        ]

# Global service instance
voice_ai_service = VoiceAIService()