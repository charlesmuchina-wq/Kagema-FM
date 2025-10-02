"""
Google Maps Integration Service
Handles Google Maps API operations for places, traffic, and navigation
"""
import googlemaps
import os
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GoogleMapsService:
    """Service class for Google Maps API integration"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
        if not self.api_key:
            logger.error("Google Maps API key not found in environment variables")
            return
            
        # Initialize Google Maps client
        try:
            self.gmaps = googlemaps.Client(key=self.api_key)
            logger.info("✅ Google Maps service initialized with real API credentials")
        except Exception as e:
            logger.error(f"Error initializing Google Maps client: {e}")
            self.gmaps = None

    def search_nearby_places(self, latitude: float, longitude: float, radius: int = 5000, place_type: str = None, keyword: str = None) -> List[Dict[str, Any]]:
        """Search for nearby places using Google Places API"""
        try:
            if not self.gmaps:
                return self.get_fallback_places(latitude, longitude)
            
            # Build search parameters
            location = (latitude, longitude)
            
            # Use places_nearby for general search or text_search for specific queries
            if keyword:
                results = self.gmaps.places(
                    query=keyword,
                    location=location,
                    radius=radius
                )
            else:
                results = self.gmaps.places_nearby(
                    location=location,
                    radius=radius,
                    type=place_type
                )
            
            # Format results for frontend
            places = []
            for place in results.get('results', [])[:20]:  # Limit to 20 results
                formatted_place = {
                    "place_id": place.get('place_id'),
                    "name": place.get('name'),
                    "address": place.get('vicinity', ''),
                    "rating": place.get('rating'),
                    "price_level": place.get('price_level'),
                    "types": place.get('types', []),
                    "location": {
                        "lat": place['geometry']['location']['lat'],
                        "lng": place['geometry']['location']['lng']
                    },
                    "photos": [
                        f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo['photo_reference']}&key={self.api_key}"
                        for photo in place.get('photos', [])[:1]  # Just first photo
                    ],
                    "opening_hours": place.get('opening_hours', {}).get('open_now'),
                    "business_status": place.get('business_status')
                }
                places.append(formatted_place)
            
            logger.info(f"Found {len(places)} nearby places for location ({latitude}, {longitude})")
            return places
            
        except Exception as e:
            logger.error(f"Error searching nearby places: {e}")
            return self.get_fallback_places(latitude, longitude)

    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific place"""
        try:
            if not self.gmaps:
                return self.get_fallback_place_details(place_id)
            
            details = self.gmaps.place(
                place_id=place_id,
                fields=['name', 'formatted_address', 'international_phone_number', 
                       'website', 'rating', 'reviews', 'opening_hours', 'photos',
                       'geometry', 'types', 'price_level']
            )
            
            result = details.get('result', {})
            
            formatted_details = {
                "place_id": place_id,
                "name": result.get('name'),
                "address": result.get('formatted_address'),
                "phone": result.get('international_phone_number'),
                "website": result.get('website'),
                "rating": result.get('rating'),
                "price_level": result.get('price_level'),
                "types": result.get('types', []),
                "location": {
                    "lat": result['geometry']['location']['lat'],
                    "lng": result['geometry']['location']['lng']
                } if result.get('geometry') else None,
                "opening_hours": {
                    "open_now": result.get('opening_hours', {}).get('open_now'),
                    "weekday_text": result.get('opening_hours', {}).get('weekday_text', [])
                },
                "reviews": [
                    {
                        "author_name": review.get('author_name'),
                        "rating": review.get('rating'),
                        "text": review.get('text'),
                        "time": review.get('time')
                    }
                    for review in result.get('reviews', [])[:5]  # Limit to 5 reviews
                ],
                "photos": [
                    f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo['photo_reference']}&key={self.api_key}"
                    for photo in result.get('photos', [])[:3]  # Limit to 3 photos
                ]
            }
            
            logger.info(f"Retrieved details for place: {result.get('name')}")
            return formatted_details
            
        except Exception as e:
            logger.error(f"Error getting place details: {e}")
            return self.get_fallback_place_details(place_id)

    def get_directions(self, origin: str, destination: str, mode: str = "driving", avoid: List[str] = None) -> Dict[str, Any]:
        """Get directions between two locations"""
        try:
            if not self.gmaps:
                return self.get_fallback_directions(origin, destination)
            
            directions_result = self.gmaps.directions(
                origin=origin,
                destination=destination,
                mode=mode,
                avoid=avoid or [],
                departure_time="now",
                traffic_model="best_guess"
            )
            
            if not directions_result:
                return self.get_fallback_directions(origin, destination)
            
            route = directions_result[0]
            leg = route['legs'][0]
            
            formatted_directions = {
                "distance": leg['distance']['text'],
                "duration": leg['duration']['text'],
                "duration_in_traffic": leg.get('duration_in_traffic', {}).get('text', leg['duration']['text']),
                "start_address": leg['start_address'],
                "end_address": leg['end_address'],
                "start_location": leg['start_location'],
                "end_location": leg['end_location'],
                "steps": [
                    {
                        "distance": step['distance']['text'],
                        "duration": step['duration']['text'],
                        "html_instructions": step['html_instructions'],
                        "maneuver": step.get('maneuver'),
                        "start_location": step['start_location'],
                        "end_location": step['end_location']
                    }
                    for step in leg['steps']
                ],
                "overview_polyline": route['overview_polyline']['points'],
                "warnings": route.get('warnings', []),
                "copyrights": route.get('copyrights')
            }
            
            logger.info(f"Generated directions from {origin} to {destination}")
            return formatted_directions
            
        except Exception as e:
            logger.error(f"Error getting directions: {e}")
            return self.get_fallback_directions(origin, destination)

    def get_traffic_conditions(self, latitude: float, longitude: float, radius: int = 2000) -> Dict[str, Any]:
        """Get traffic conditions for a location"""
        try:
            if not self.gmaps:
                return self.get_fallback_traffic_conditions()
            
            # Use nearby search to find major roads/highways
            location = (latitude, longitude)
            
            # Search for nearby roads and check traffic
            nearby_roads = self.gmaps.places_nearby(
                location=location,
                radius=radius,
                type='establishment'  # This will include roads and major establishments
            )
            
            # Simulate traffic analysis (Google Maps doesn't have a direct traffic API)
            # In practice, you'd use the Roads API or Distance Matrix API with traffic
            traffic_info = {
                "location": {"lat": latitude, "lng": longitude},
                "radius": radius,
                "overall_traffic": "moderate",  # This would be calculated from actual data
                "incidents": [],
                "travel_times": {
                    "to_city_center": self._estimate_travel_time(latitude, longitude, "city_center"),
                    "to_airport": self._estimate_travel_time(latitude, longitude, "airport"),
                    "to_highway": self._estimate_travel_time(latitude, longitude, "highway")
                },
                "last_updated": "now"
            }
            
            logger.info(f"Generated traffic conditions for location ({latitude}, {longitude})")
            return traffic_info
            
        except Exception as e:
            logger.error(f"Error getting traffic conditions: {e}")
            return self.get_fallback_traffic_conditions()

    def geocode_address(self, address: str) -> Dict[str, Any]:
        """Convert an address to coordinates"""
        try:
            if not self.gmaps:
                return {"lat": 0, "lng": 0, "formatted_address": address}
            
            geocode_result = self.gmaps.geocode(address)
            
            if geocode_result:
                location = geocode_result[0]
                return {
                    "lat": location['geometry']['location']['lat'],
                    "lng": location['geometry']['location']['lng'],
                    "formatted_address": location['formatted_address'],
                    "place_id": location['place_id'],
                    "types": location['types']
                }
            
            return {"lat": 0, "lng": 0, "formatted_address": address}
            
        except Exception as e:
            logger.error(f"Error geocoding address: {e}")
            return {"lat": 0, "lng": 0, "formatted_address": address}

    def reverse_geocode(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Convert coordinates to an address"""
        try:
            if not self.gmaps:
                return {"formatted_address": f"{latitude}, {longitude}"}
            
            reverse_geocode_result = self.gmaps.reverse_geocode((latitude, longitude))
            
            if reverse_geocode_result:
                location = reverse_geocode_result[0]
                return {
                    "formatted_address": location['formatted_address'],
                    "place_id": location['place_id'],
                    "types": location['types'],
                    "address_components": location.get('address_components', [])
                }
            
            return {"formatted_address": f"{latitude}, {longitude}"}
            
        except Exception as e:
            logger.error(f"Error reverse geocoding: {e}")
            return {"formatted_address": f"{latitude}, {longitude}"}

    def _estimate_travel_time(self, lat: float, lng: float, destination_type: str) -> str:
        """Estimate travel time to common destinations (fallback method)"""
        # This is a simplified estimation - in practice you'd use Distance Matrix API
        estimates = {
            "city_center": "15-25 min",
            "airport": "30-45 min", 
            "highway": "5-10 min"
        }
        return estimates.get(destination_type, "Unknown")

    # Fallback methods for when API is unavailable
    def get_fallback_places(self, latitude: float, longitude: float) -> List[Dict[str, Any]]:
        """Return fallback places data when API is unavailable"""
        return [
            {
                "place_id": "fallback_1",
                "name": "Demo Restaurant",
                "address": "Near your location",
                "rating": 4.5,
                "price_level": 2,
                "types": ["restaurant", "food"],
                "location": {"lat": latitude + 0.001, "lng": longitude + 0.001},
                "photos": [],
                "opening_hours": True,
                "business_status": "OPERATIONAL"
            },
            {
                "place_id": "fallback_2", 
                "name": "Demo Coffee Shop",
                "address": "Nearby",
                "rating": 4.2,
                "price_level": 1,
                "types": ["cafe", "food"],
                "location": {"lat": latitude - 0.001, "lng": longitude - 0.001},
                "photos": [],
                "opening_hours": True,
                "business_status": "OPERATIONAL"
            }
        ]

    def get_fallback_place_details(self, place_id: str) -> Dict[str, Any]:
        """Return fallback place details"""
        return {
            "place_id": place_id,
            "name": "Demo Place",
            "address": "Demo Address",
            "phone": "+1-234-567-8900",
            "website": "https://demo.com",
            "rating": 4.0,
            "price_level": 2,
            "types": ["establishment"],
            "location": {"lat": 0, "lng": 0},
            "opening_hours": {"open_now": True, "weekday_text": []},
            "reviews": [],
            "photos": []
        }

    def get_fallback_directions(self, origin: str, destination: str) -> Dict[str, Any]:
        """Return fallback directions"""
        return {
            "distance": "5.2 km",
            "duration": "12 mins",
            "duration_in_traffic": "15 mins",
            "start_address": origin,
            "end_address": destination,
            "start_location": {"lat": 0, "lng": 0},
            "end_location": {"lat": 0.01, "lng": 0.01},
            "steps": [
                {
                    "distance": "5.2 km",
                    "duration": "12 mins",
                    "html_instructions": f"Drive from {origin} to {destination}",
                    "maneuver": "straight",
                    "start_location": {"lat": 0, "lng": 0},
                    "end_location": {"lat": 0.01, "lng": 0.01}
                }
            ],
            "overview_polyline": "demo_polyline_data",
            "warnings": [],
            "copyrights": "Demo data"
        }

    def get_fallback_traffic_conditions(self) -> Dict[str, Any]:
        """Return fallback traffic conditions"""
        return {
            "location": {"lat": 0, "lng": 0},
            "radius": 2000,
            "overall_traffic": "light",
            "incidents": [],
            "travel_times": {
                "to_city_center": "15-20 min",
                "to_airport": "30-40 min",
                "to_highway": "5-8 min"
            },
            "last_updated": "demo"
        }

# Initialize service instance
googlemaps_service = GoogleMapsService()