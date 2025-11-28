"""
FastAPI Backend for Route Optimization

Provides REST API endpoints for running route optimization algorithms
and returning results with visualization coordinates.

Uses Google Maps API for real city data.
Make sure GOOGLE_MAPS_API_KEY is set in .env or environment variables.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'graph'))
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'graph'))

from graph.route_optimizer import RouteOptimizer
from graph.city_graph import initialize_city_graph

# Initialize city graph with Google Maps API
# This will check for cached data first, then fetch from API if needed
print("Initializing city graph...")
city_graph = None
try:
    city_graph = initialize_city_graph(use_cache=True)
    print(f"✓ Initialized: {city_graph}")
except Exception as e:
    print(f"✗ Error initializing city graph: {e}")
    print("\nMake sure GOOGLE_MAPS_API_KEY is set:")
    print("  - Add to .env file: GOOGLE_MAPS_API_KEY=your_key_here")
    print("  - Or set environment variable: export GOOGLE_MAPS_API_KEY=your_key_here")

# Create FastAPI app
app = FastAPI(
    title="Route Optimization API",
    description="Compare A*, UCS, and Greedy search algorithms for route finding",
    version="1.0.0"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class RouteRequest(BaseModel):
    """Request to find routes between two cities."""
    initial_city: str
    goal_city: str


class CityLocation(BaseModel):
    """City location for map visualization."""
    name: str
    lat: float
    lon: float


class PathResult(BaseModel):
    """Result from a single algorithm."""
    algorithm: str
    path: List[str]
    total_distance: float
    nodes_expanded: int
    execution_time_ms: float
    success: bool
    path_coordinates: List[Dict[str, float]]


class RouteResponse(BaseModel):
    """Response containing results from all three algorithms."""
    initial_city: str
    goal_city: str
    initial_coordinates: Dict[str, float]
    goal_coordinates: Dict[str, float]
    results: Dict[str, PathResult]


# Helper functions
def get_city_coordinates(city_name: str) -> Dict[str, float]:
    """Get lat/lon coordinates for a city."""
    lat, lon = city_graph.get_coordinates(city_name)
    return {"lat": lat, "lon": lon}


def get_path_coordinates(path: List[str]) -> List[Dict[str, float]]:
    """Convert path of city names to list of coordinates."""
    coordinates = []
    for city in path:
        lat, lon = city_graph.get_coordinates(city)
        coordinates.append({"lat": lat, "lon": lon})
    return coordinates


# API Endpoints

@app.get("/")
def read_root():
    """Root endpoint with API information."""
    if city_graph is None:
        return {
            "error": "City graph not initialized",
            "message": "Set GOOGLE_MAPS_API_KEY environment variable"
        }
    return {
        "name": "Route Optimization API",
        "description": "Compare A*, UCS, and Greedy pathfinding algorithms",
        "endpoints": {
            "cities": "/cities - List all available cities",
            "routes": "/routes - POST to find routes between cities",
            "health": "/health - Health check"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    if city_graph is None:
        return {
            "status": "error",
            "message": "City graph not initialized",
            "version": "1.0.0"
        }
    return {"status": "healthy", "version": "1.0.0"}


# @app.get("/cities")
# def list_cities():
#     """Get list of all available cities."""
#     if city_graph is None:
#         raise HTTPException(
#             status_code=500,
#             detail="City graph not initialized. Set GOOGLE_MAPS_API_KEY environment variable."
#         )
#     cities = sorted(city_graph.get_all_cities())
#     return {
#         "cities": cities,
#         "count": len(cities)
#     }



@app.post("/routes", response_model=RouteResponse)
def find_routes(request: RouteRequest):
    """
    Find routes between two cities using all three algorithms.
    
    Automatically geocodes cities if they don't exist yet.
    
    Args:
        request: RouteRequest with initial_city and goal_city
    
    Returns:
        RouteResponse with results from all three algorithms
    """
    if city_graph is None:
        raise HTTPException(
            status_code=500,
            detail="City graph not initialized. Set GOOGLE_MAPS_API_KEY environment variable."
        )
    
    initial_city = request.initial_city.strip()
    goal_city = request.goal_city.strip()
    
    if initial_city == goal_city:
        raise HTTPException(
            status_code=400,
            detail="Initial and goal cities must be different"
        )
    
    try:
        if initial_city not in city_graph.get_all_cities():
            print(f"Geocoding {initial_city}...")
            city_graph.add_city(initial_city)
        if goal_city not in city_graph.get_all_cities():
            print(f"Geocoding {goal_city}...")
            city_graph.add_city(goal_city)
        
        # Verify cities were added successfully
        if initial_city not in city_graph.get_all_cities():
            raise HTTPException(
                status_code=400,
                detail=f"Could not find coordinates for '{initial_city}'",
            )
        if goal_city not in city_graph.get_all_cities():
            raise HTTPException(
                status_code=400, 
                detail=f"Could not find coordinates for '{goal_city}'"
            )
        
        # Build dynamic network between cities
        print(f"\nBuilding network for {initial_city} → {goal_city}...")
        city_graph.build_dynamic_network(initial_city, goal_city, num_intermediate=12)
            
        results = RouteOptimizer.run_all_algorithms(initial_city, goal_city, city_graph)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing route: {str(e)}"
        )
    
    # Format results
    formatted_results = {}
    for algo_key, algo_result in results.items():
        formatted_results[algo_key] = PathResult(
            algorithm=algo_result.algorithm_name,
            path=algo_result.path,
            total_distance=algo_result.path_cost,
            nodes_expanded=algo_result.nodes_expanded,
            execution_time_ms=algo_result.execution_time_ms,
            success=algo_result.success,
            path_coordinates=get_path_coordinates(algo_result.path)
        )
    
    return RouteResponse(
        initial_city=initial_city,
        goal_city=goal_city,
        initial_coordinates=get_city_coordinates(initial_city),
        goal_coordinates=get_city_coordinates(goal_city),
        results=formatted_results
    )

@app.get("/routes/{initial}/{goal}")
def find_routes_get(initial: str, goal: str):
    """
    Alternative GET endpoint for finding routes (for easier testing).
    
    Usage: /routes/Buffalo/NYC
    """
    return find_routes(RouteRequest(initial_city=initial, goal_city=goal))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)