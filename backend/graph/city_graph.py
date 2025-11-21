"""
NYC Metropolitan Route Optimization - City Data with Google Maps API

This module creates a city graph for New York State using Google Maps API:
- Fetches real city coordinates using Geocoding API
- Calculates real driving distances using Distance Matrix API
- Creates a graph of cities with realistic road networks

Requires a Google Maps API key with:
  - Geocoding API enabled
  - Distance Matrix API enabled
  - Maps SDK enabled

Set your API key as environment variable:
  export GOOGLE_MAPS_API_KEY="your_api_key_here"

Or add to .env file:
  GOOGLE_MAPS_API_KEY=your_api_key_here
"""

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
    Represents New York State cities as a graph using Google Maps API.
    
    Uses Google Maps Geocoding API to get coordinates and Distance Matrix API
    to get real driving distances.
    
    Attributes:
        api_key: Google Maps API key
        gmaps: Google Maps client
        cities: Dict mapping city names to (latitude, longitude) tuples
        graph: Dict mapping city names to dicts of neighbors and distances
        cache_file: JSON file for caching API results (to avoid rate limits)
    """
    
    def __init__(self, api_key: Optional[str] = None, use_cache: bool = True):
        """
        Initialize the NY State city graph with Google Maps API.
        
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
        
        # Try to load from cache first
        if use_cache and os.path.exists(self.cache_file):
            print(f"Loading cached city data from {self.cache_file}...")
            self._load_from_cache()
        else:
            print("Initializing Google Maps client...")
            if googlemaps is None:
                raise ImportError("googlemaps library required. Run: pip install googlemaps")
            
            self.gmaps = googlemaps.Client(key=api_key)
            print("Fetching city coordinates and distances from Google Maps API...")
            self._initialize_from_api()
            self._save_to_cache()
    
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
    
    # def _initialize_from_api(self):
    #     """Fetch city coordinates and distances from Google Maps API."""
        
    #     # List of NY State cities to include
    #     ny_cities = [
    #         "Buffalo, NY",
    #         "Rochester, NY",
    #         "Syracuse, NY",
    #         "Albany, NY",
    #         "New York City, NY",
    #         "Yonkers, NY",
    #         "Niagara Falls, NY",
    #         "Utica, NY",
    #         "Schenectady, NY",
    #         "Glens Falls, NY",
    #         "Plattsburgh, NY",
    #         "Watertown, NY",
    #         "Oswego, NY",
    #         "Ithaca, NY",
    #         "Binghamton, NY",
    #         "Elmira, NY",
    #         "Corning, NY",
    #         "Olean, NY",
    #         "Batavia, NY",
    #         "Kingston, NY",
    #         "New Rochelle, NY",
    #     ]
        
    #     # Fetch coordinates for each city
    #     print("Geocoding cities...")
    #     for city_full in ny_cities:
    #         try:
    #             # Extract short name (e.g., "Buffalo" from "Buffalo, NY")
    #             city_name = city_full.split(",")[0]
                
    #             # Geocode the city
    #             geocode_result = self.gmaps.geocode(city_full)
                
    #             if geocode_result:
    #                 location = geocode_result[0]['geometry']['location']
    #                 lat, lng = location['lat'], location['lng']
    #                 self.cities[city_name] = (lat, lng)
    #                 print(f"  ✓ {city_name}: ({lat:.4f}, {lng:.4f})")
    #             else:
    #                 print(f"  ✗ {city_name}: Not found")
            
    #         except Exception as e:
    #             print(f"  ✗ {city_name}: Error - {e}")
        
    #     # Initialize graph structure
    #     city_list = list(self.cities.keys())
    #     for city in city_list:
    #         self.graph[city] = {}
        
    #     # Fetch distances between cities using Distance Matrix API
    #     print("\nFetching distances between cities...")
    #     self._fetch_distances(city_list)
    
    
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
    def _fetch_distances(self, cities: list):
        """
        Fetch driving distances between cities using Google Distance Matrix API.
        
        The Distance Matrix API allows up to 25 origins × 25 destinations per request.
        """
        
        # Distance Matrix API limit: 25x25
        batch_size = 10
        
        for i in range(0, len(cities), batch_size):
            origins = cities[i:i+batch_size]
            destinations = cities[i:i+batch_size]
            
            try:
                # Call Distance Matrix API
                result = self.gmaps.distance_matrix(
                    origins=origins,
                    destinations=destinations,
                    mode="driving",
                    units="imperial"  # Miles
                )
                
                # Parse results
                for origin_idx, origin in enumerate(origins):
                    for dest_idx, destination in enumerate(destinations):
                        if origin != destination:
                            try:
                                element = result['rows'][origin_idx]['elements'][dest_idx]
                                
                                if element['status'] == 'OK':
                                    # Distance in miles
                                    distance = element['distance']['value'] / 1609.34
                                    
                                    # Only add edge if not already present (undirected)
                                    if destination not in self.graph[origin]:
                                        self.graph[origin][destination] = distance
                                    
                                    print(f"  {origin} → {destination}: {distance:.0f} miles")
                                else:
                                    print(f"  ✗ {origin} → {destination}: {element['status']}")
                            
                            except (KeyError, IndexError) as e:
                                print(f"  ✗ Error parsing distance for {origin} → {destination}")
            
            except Exception as e:
                print(f"Error fetching distances: {e}")
    
    def get_neighbors(self, city: str) -> Dict[str, float]:
        """
        Get all neighboring cities and distances from a given city.
        
        Args:
            city: City name (string)
        
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
        using the Haversine formula.
        
        This is used as the heuristic function for A* search.
        
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
    
    def get_all_cities(self):
        """Return list of all cities in the graph."""
        return list(self.cities.keys())
    
    def __repr__(self):
        """String representation showing number of cities and edges."""
        num_edges = sum(len(neighbors) for neighbors in self.graph.values()) // 2
        return f"CityGraph({len(self.cities)} cities, {num_edges} connections)"


# Singleton instance for use throughout the application
# Note: This will only be created when explicitly imported and initialized
city_graph = None


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
    global city_graph
    city_graph = CityGraph(api_key=api_key, use_cache=use_cache)
    return city_graph