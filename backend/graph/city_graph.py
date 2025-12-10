
import os
import math
import json
from typing import Dict, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    import googlemaps
except ImportError:
    print("ERROR: googlemaps not installed. Run: pip install googlemaps")
    googlemaps = None


class CityGraph:
    """
    Represents cities as a graph using Google Maps API.
    
    Uses Google Maps Geocoding API to get coordinates and Distance Matrix API
    to get real driving distances. Dynamically builds networks on demand.
    
    Attributes:
        api_key: Google Maps API key
        gmaps: Google Maps client
        cities: Dict mapping city names to (latitude, longitude) tuples
        graph: Dict mapping city names to dicts of neighbors and distances
        cache_file: JSON file for caching API results
    """
    
    def __init__(self, api_key: Optional[str] = None, use_cache: bool = True):
        """
        Initialize the city graph with Google Maps API.
        
        Args:
            api_key: Google Maps API key. If None, reads from GOOGLE_MAPS_API_KEY env var
            use_cache: If True, loads cached results to avoid API calls
        
        Raises:
            ValueError: If API key not provided and not in environment
        """
        # Get API key
        if api_key is None:
            api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
        if not api_key:
            raise ValueError(
                "Google Maps API key not found. Set GOOGLE_MAPS_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.api_key = api_key
        self.cache_file = "city_graph_cache.json"
        self.cities = {}
        self.graph = {}
        self.directed = False
        self.intermediate_cities = []  # Add this line
        # Initialize Google Maps client
        print("Initializing Google Maps client...")
        if googlemaps is None:
            raise ImportError("googlemaps library required. Run: pip install googlemaps")
        self.gmaps = googlemaps.Client(key=api_key)
        
        # Try to load from cache first
        if use_cache and os.path.exists(self.cache_file):
            # print(f"Loading cached city data from {self.cache_file}...")
            self._load_from_cache()
        else:
            print("Ready to add cities dynamically via add_city()")
    
    def _load_from_cache(self):
        """Load cached city and graph data from JSON file."""
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                self.cities = data.get("cities", {})
                self.graph = data.get("graph", {})
            print(f"✓ Loaded {len(self.cities)} cities from cache")
        except Exception as e:
            print(f"Error loading cache: {e}. Will fetch fresh data.")
            self.cities = {}
            self.graph = {}
    
    def _save_to_cache(self):
        """Save city and graph data to JSON file for future use."""
        try:
            data = {
                "cities": self.cities,
                "graph": self.graph
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Saved city data to {self.cache_file}")
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def add_city(self, city_name: str):
        """Dynamically add a city by geocoding it."""
        try:
            geocode_result = self.gmaps.geocode(city_name)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                lat, lng = location['lat'], location['lng']
                formatted_name = geocode_result[0]['formatted_address']
                self.cities[city_name] = (lat, lng)
                self.graph[city_name] = {}
                print(f"✓ Added {city_name}")
                print(f"  Location: {formatted_name}")
                print(f"  Coords: ({lat:.4f}, {lng:.4f})")
                return True
            else:
                print(f"✗ {city_name}: Not found in Google Maps")
                return False
        except Exception as e:
            print(f"✗ {city_name}: Error - {e}")
            return False
    
    def connect_cities(self, city1: str, city2: str):
        """Add connection between two cities with real distance."""
        try:
            # Make sure both cities exist in graph
            if city1 not in self.graph:
                self.graph[city1] = {}
            if city2 not in self.graph:
                self.graph[city2] = {}
            
            result = self.gmaps.distance_matrix(
                origins=[city1],
                destinations=[city2],
                mode="driving",
                units="imperial"
            )
            
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                distance = result['rows'][0]['elements'][0]['distance']['value'] / 1609.34
                self.graph[city1][city2] = distance
                self.graph[city2][city1] = distance
                print(f"✓ {city1} ↔ {city2}: {distance:.0f} miles")
                return True
            else:
                print(f"✗ Could not get distance")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
        
      
      
    def find_intermediate_cities(self, start_city: str, goal_city: str, num_cities):
        """
        IMPROVED VERSION:
        - Extracts state from input more robustly
        - Filters results to only cities in that state
        - Returns cities with full location info
        - DEBUGGED: Better error handling
        """
        try:
            print(f"\n🔍 Finding intermediate cities between {start_city} and {goal_city}")
            
            start_coords = self.get_coordinates(start_city)
            goal_coords = self.get_coordinates(goal_city)
            
            if not start_coords or not goal_coords:
                print("❌ Could not geocode start or goal city")
                return []
            
            start_lat, start_lon = start_coords
            goal_lat, goal_lon = goal_coords
            
            print(f"  Start: ({start_lat:.4f}, {start_lon:.4f})")
            print(f"  Goal: ({goal_lat:.4f}, {goal_lon:.4f})")
            
            start_state = None
            goal_state = None
            
            # Extract start state
            if "," in start_city:
                parts = [p.strip() for p in start_city.split(",")]
                if len(parts) >= 2:
                    start_state = parts[1]
            
            # Extract goal state
            if "," in goal_city:
                parts = [p.strip() for p in goal_city.split(",")]
                if len(parts) >= 2:
                    goal_state = parts[1]
            
            if not start_state or not goal_state:
                print("❌ Please use format: 'City, STATE' for both start and goal")
                return []
            
            print(f"  📍 Route spans: {start_state} → {goal_state}")
            
            intermediate_cities = []
            print(f"num_cities:{num_cities}\n")
            for i in range(1, num_cities + 1):
                try:
                    t = i / (num_cities + 1)
                    search_lat = start_lat + (goal_lat - start_lat) * t
                    search_lon = start_lon + (goal_lon - start_lon) * t
                    
                    print(f"\n  🔎 Search point {i}/{num_cities}: ({search_lat:.4f}, {search_lon:.4f})")
                    
                    # Search for cities near this point
                    places_result = self.gmaps.places_nearby(
                        location=(search_lat, search_lon),
                        radius=80000,  # 80km radius
                        type='locality'
                    )
                    
                    if not places_result.get('results'):
                        print(f"No places found at this point")
                        continue
                    
                    print(f"    Found {len(places_result['results'])} places")
                    
                    # ============ FILTER RESULTS ============
                    for idx, place in enumerate(places_result['results'][:5]):  # Check top 5
                        try:
                            city_name = place.get('name', '').strip()
                            place_id = place.get('place_id')

                            if not place_id: continue
                            
                            start_name = start_city.split(",")[0].strip().lower()
                            goal_name = goal_city.split(",")[0].strip().lower() 
                            
                            print(f"      Checking: {city_name}...", end=" ")
                            if city_name.lower() == start_name or city_name.lower() == goal_name:
                                print("(is start/goal city)")
                                continue

                            # Fetch full place details using place_id
                            details_result = self.gmaps.place(
                                place_id=place_id, 
                                fields=['address_component']
                            )
                            found_state = None
                            found_country = None 
                            for component in details_result['result']['address_components']:
                                if 'administrative_area_level_1' in component['types']:
                                    found_state = component['short_name'].strip()
                                if 'country' in component['types']:
                                    found_country = component['short_name'].strip()

                            if found_country not in ['US', 'CA']:
                                print(f"(skipping country: {found_country})")
                                continue
                            # 1. Reject cities if they are neither US nor CA (e.g., Mexico, Europe)
                            if found_country == 'CA':
                                # E.g., Toronto, ON (CA)
                                full_city = f"{city_name}, {found_state} (CA)"
                            elif found_state:
                                # E.g., Buffalo, NY
                                full_city = f"{city_name}, {found_state}"
                            else:
                                # Fallback for places with no admin level 1 (shouldn't happen for locality)
                                full_city = f"{city_name}, {found_country}"
                            
                            if full_city in intermediate_cities:
                                print(f"(duplicate: {full_city})")
                                continue

                            

                            if self.add_city(full_city):
                                city_coords = self.get_coordinates(full_city)
                                if city_coords:
                                    city_lat, city_lon = city_coords
                                    lat_min, lat_max = min(start_lat, goal_lat), max(start_lat, goal_lat)
                                    lon_min, lon_max = min(start_lon, goal_lon), max(start_lon, goal_lon)
                                    tolerance = 3 if abs(goal_lat - start_lat) > 2 else 1
                                    lat_in_range = lat_min - tolerance <= city_lat <= lat_max + tolerance
                                    lon_in_range = lon_min - tolerance <= city_lon <= lon_max + tolerance
                                    
                                    if not (lat_in_range and lon_in_range):
                                        print(f"(off route)")
                                        continue
                                    intermediate_cities.append(full_city)
                                    print(f"    ✓ ADDED: {full_city}")
                                    break  # Move to the next search point
                            else:
                                print(f"(failed to add to graph)")
                        except Exception as e:
                            print(f"(error: {str(e)[:40]})")
                            continue
                
                except Exception as e:
                    print(f"  Error at search point {i}: {e}")
                    continue
            
            print(f"\n✅ Found {len(intermediate_cities)} intermediate cities:")
            # for city in intermediate_cities:
            #     print(f"   - {city}")
            
            return intermediate_cities[:num_cities]
        
        except Exception as e:
            print(f"❌ CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            return []

 
    def build_dynamic_network(self, start_city: str, goal_city: str, num_intermediate: int = 25):
        """
        Build a dynamic network by finding intermediate cities and connecting nearby ones.
        
        Args:
            start_city: Starting city
            goal_city: Goal city
            num_intermediate: Number of intermediate cities to find
        """
        print(f"\n🌍 Building dynamic network from {start_city} to {goal_city}...")
        
        # Add start and goal if not present
        if start_city not in self.get_all_cities():
            self.add_city(start_city)
        if goal_city not in self.get_all_cities():
            self.add_city(goal_city)
        
        # Find intermediate cities
        intermediate = self.find_intermediate_cities(start_city, goal_city, num_intermediate)
        self.intermediate_cities= intermediate
        # Add all intermediate cities
        for city in intermediate:
            if city not in self.get_all_cities():
                self.add_city(city)
        
        # Build ordered list: start → intermediate → goal
        all_cities = [start_city] + intermediate + [goal_city]
        
        # Connect nearby cities (create multiple paths)
        print(f"\n🔗 Connecting nearby cities...")
        for i, city1 in enumerate(all_cities):
            # Connect to next few cities (create multiple paths)
            for city2 in all_cities[i+1:i+4]:  # Connect to next 3 cities
                if city2 not in self.get_neighbors(city1):
                    self.connect_cities(city1, city2)
        
        print(f"✓ Network built with {len(all_cities)} cities")
        return all_cities, intermediate
    
    def get_neighbors(self, city: str) -> Dict[str, float]:
        """
        Get all neighboring cities and distances from a given city.
        
        Args:
            city: City name
        
        Returns:
            Dict mapping neighbor city names to distances
        """
        return self.graph.get(city, {})
    
    def get_distance(self, city1: str, city2: str) -> Optional[float]:
        """
        Get direct distance between two connected cities.
        
        Args:
            city1: Source city name
            city2: Destination city name
        
        Returns:
            Distance in miles, or None if not directly connected
        """
        return self.graph.get(city1, {}).get(city2, None)
    
    def get_coordinates(self, city: str) -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude coordinates for a city.
        
        Args:
            city: City name
        
        Returns:
            Tuple of (latitude, longitude)
        """
        return self.cities.get(city)
    
    def haversine_distance(self, city1: str, city2: str) -> float:
        """
        Calculate straight-line distance (as crow flies) between two cities
        using the Haversine formula. Used as heuristic for A* search.
        
        Args:
            city1: First city name
            city2: Second city name
        
        Returns:
            Approximate distance in miles
        """
        coords1 = self.get_coordinates(city1)
        coords2 = self.get_coordinates(city2)
        
        if not coords1 or not coords2:
            return 0
        
        lat1, lon1 = coords1
        lat2, lon2 = coords2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in miles
        r = 3959
        
        return c * r
    

    
    def euclidean_distance(self, city1: str, city2: str) -> float:
        """Euclidean distance"""
        lat1, lon1 = self.get_coordinates(city1)
        lat2, lon2 = self.get_coordinates(city2)
        if not (lat1 and lon2):
            return 0
        # Approximate: 1 degree latitude ≈ 69 miles
        return ((lat2 - lat1)**2 + (lon2 - lon1)**2)**0.5 * 69
    
    def manhattan_distance(self, city1: str, city2: str) -> float:
        """Manhattan distance (taxicab metric)"""
        lat1, lon1 = self.get_coordinates(city1)
        lat2, lon2 = self.get_coordinates(city2)
        if not (lat1 and lon2):
            return 0
        return (abs(lat2 - lat1) + abs(lon2 - lon1)) * 69
    
    def min_graph_distance(self, city1: str, city2: str) -> float:
        """Minimum cost edge from current city"""
        neighbors = self.get_neighbors(city1)
        if not neighbors:
            return 0
        return min(neighbors.values())
    
    def weighted_heuristic(self, city1: str, city2: str) -> float:
        """Weighted combination of heuristics"""
        h_distance = self.haversine_distance(city1, city2)
        h_graph = self.min_graph_distance(city1, city2)
        alpha = 0.7  # 70% distance, 30% graph
        return alpha * h_distance + (1 - alpha) * h_graph


    def get_all_cities(self):
        """Return list of all cities in the graph."""
        return list(self.cities.keys())
    
    def __repr__(self):
        """String representation showing number of cities and edges."""
        num_edges = sum(len(neighbors) for neighbors in self.graph.values()) // 2
        return f"CityGraph({len(self.cities)} cities, {num_edges} connections)"


def initialize_city_graph(api_key: Optional[str] = None, use_cache: bool = True) -> CityGraph:
    """
    Initialize the global city graph instance.
    
    Args:
        api_key: Google Maps API key (optional, reads from environment if not provided)
        use_cache: Use cached data if available
    
    Returns:
        Initialized CityGraph instance
    
    Example:
        >>> from city_graph import initialize_city_graph
        >>> graph = initialize_city_graph()
        >>> print(graph)
    """
    return CityGraph(api_key=api_key, use_cache=use_cache)