"""
NYC Metropolitan Route Optimization - City Data

This module contains the city graph for New York State with:
- City names and geographic coordinates (lat, long)
- Direct connections between cities
- Approximate driving distances between connected cities
- Haversine distance calculation for A* heuristic

Cities are represented as nodes in an undirected graph.
A state in this problem is simply a city name (string).
"""

import math
from typing import Dict, Tuple


class CityGraph:
    """
    Represents New York State cities as a graph.
    
    Attributes:
        cities: Dict mapping city names to (latitude, longitude) tuples
        graph: Dict mapping city names to dicts of neighbors and distances
        directed: Boolean indicating if graph is directed (False for undirected)
    """
    
    def __init__(self):
        """Initialize the NY State city graph with coordinates and connections."""
        
        # City coordinates (latitude, longitude) - approximate
        self.cities = {
            "Buffalo": (42.8864, -78.8784),
            "Niagara Falls": (43.0896, -79.0849),
            "Rochester": (43.1629, -77.6111),
            "Syracuse": (43.0481, -76.1474),
            "Utica": (43.1010, -75.2231),
            "Binghamton": (42.0987, -75.9180),
            "Albany": (42.6526, -73.7562),
            "Schenectady": (42.8142, -73.9396),
            "Glens Falls": (43.3196, -73.6433),
            "Plattsburgh": (44.7597, -73.4570),
            "Watertown": (43.9747, -75.9108),
            "Oswego": (43.4673, -76.5107),
            "Ithaca": (42.4534, -76.4735),
            "Elmira": (42.1105, -76.8073),
            "Corning": (42.1407, -77.0508),
            "Olean": (42.0823, -78.4305),
            "Batavia": (42.9861, -78.1848),
            "NYC": (40.7128, -74.0060),
            "Yonkers": (40.8448, -73.8648),
            "New Rochelle": (40.8819, -73.7878),
            "Kingston": (41.9276, -74.0149),
        }
        
        # Build the graph: city -> {neighbor: distance}
        # Distances are approximate driving distances in miles
        self.graph = {}
        self._initialize_graph()
        
        self.directed = False
    
    def _initialize_graph(self):
        """Initialize graph connections with approximate driving distances."""
        
        # Define connections as (city1, city2, distance_in_miles)
        connections = [
            # Western NY
            ("Buffalo", "Niagara Falls", 25),
            ("Buffalo", "Rochester", 85),
            ("Buffalo", "Batavia", 35),
            ("Niagara Falls", "Batavia", 55),
            
            # Central NY
            ("Rochester", "Syracuse", 85),
            ("Rochester", "Batavia", 50),
            ("Syracuse", "Utica", 50),
            ("Syracuse", "Albany", 170),
            ("Syracuse", "Oswego", 35),
            ("Oswego", "Utica", 90),
            
            # Southern Tier
            ("Binghamton", "Utica", 120),
            ("Binghamton", "Ithaca", 75),
            ("Ithaca", "Elmira", 70),
            ("Elmira", "Corning", 30),
            ("Corning", "Olean", 90),
            ("Olean", "Buffalo", 100),
            
            # Eastern NY
            ("Schenectady", "Albany", 15),
            ("Glens Falls", "Albany", 60),
            ("Glens Falls", "Plattsburgh", 100),
            ("Watertown", "Plattsburgh", 130),
            ("Plattsburgh", "Schenectady", 250),
            
            # Downstate
            ("NYC", "Yonkers", 20),
            ("NYC", "New Rochelle", 25),
            ("NYC", "Kingston", 90),
            ("Kingston", "Albany", 90),
            ("Yonkers", "New Rochelle", 20),
            
            # Connectors
            ("Albany", "Utica", 90),
            ("Kingston", "Schenectady", 110),
        ]
        
        # Initialize all cities with empty neighbor dicts
        for city in self.cities:
            self.graph[city] = {}
        
        # Add connections (bidirectional for undirected graph)
        for city1, city2, distance in connections:
            self.graph[city1][city2] = distance
            self.graph[city2][city1] = distance  # Undirected graph
    
    def get_neighbors(self, city: str) -> Dict[str, float]:
        """
        Get all neighboring cities and distances from a given city.
        
        Args:
            city: City name (string)
        
        Returns:
            Dict mapping neighbor city names to distances
        """
        return self.graph.get(city, {})
    
    def get_distance(self, city1: str, city2: str) -> float:
        """
        Get direct distance between two connected cities.
        
        Args:
            city1: Source city name
            city2: Destination city name
        
        Returns:
            Distance in miles, or None if not directly connected
        """
        return self.graph.get(city1, {}).get(city2, None)
    
    def get_coordinates(self, city: str) -> Tuple[float, float]:
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


# Create a singleton instance for use throughout the application
city_graph = CityGraph()