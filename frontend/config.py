"""
Configuration and constants for Route Optimization application.
"""
import os

# API Configuration
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# API_URL = "https://routing-intelligence-backend.onrender.com"
if os.environ.get("RENDER") == "true":
    API_URL = "https://routing-intelligence-backend.onrender.com"

# Algorithm Colors (for map visualization)
ALGORITHM_COLORS = {
    "ucs": "#4285F4",      # Blue
    "astar": "#EA4335",    # Red
    "greedy": "#34A853",   # Green
    "dfs": "#FBBC04"       # Yellow
}

# Algorithm Display Names
ALGORITHM_NAMES = {
    "ucs": "UCS (Dijkstra)",
    "astar": "A* Search",
    "greedy": "Greedy Best-First",
    "dfs": "Depth-First Search"
}

# Algorithm Descriptions
ALGORITHM_DESCRIPTIONS = {
    "ucs": "Uniform Cost Search - Expands nodes based on total distance traveled. Guarantees optimal path.",
    "astar": "A* Search - Expands nodes based on distance + heuristic estimate. Optimal and efficient.",
    "greedy": "Greedy Best-First - Expands nodes based only on heuristic estimate. Fastest but may be suboptimal.",
    "dfs": "Depth-First Search - Expands deepest nodes first. Very fast but doesn't guarantee optimal path."
}

# Map Configuration
MAP_CENTER_LAT = 39.5
MAP_CENTER_LON = -98.0
MAP_ZOOM_START = 4

# UI Configuration
PAGE_TITLE = "Route Optimization: Algorithm Comparison"
PAGE_ICON = "🗺️"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Default Cities
DEFAULT_FROM_CITY = "Potsdam, NY"
DEFAULT_TO_CITY = "Austin, TX"

# Network Configuration
DEFAULT_NUM_INTERMEDIATE = 25
API_TIMEOUT = 60