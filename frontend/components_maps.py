"""
Map display component - Google Maps with toggleable algorithm paths.
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import os
from config import ALGORITHM_COLORS, ALGORITHM_NAMES


def _format_algo_name(algo_key: str) -> str:
    """Convert algo_key to readable name"""
    mapping = {
        'ucs': 'UCS (Dijkstra)',
        'astar_haversine': 'A* (Haversine)',
        'astar_euclidean': 'A* (Euclidean)',
        'astar_manhattan': 'A* (Manhattan)',
        'astar_min_graph': 'A* (Min Graph)',
        'astar_weighted': 'A* (Weighted)',
        'greedy': 'Greedy Best-First',
        'dfs': 'DFS',
    }
    return mapping.get(algo_key, algo_key)


def _get_algo_color(algo_key: str) -> str:
    """Get color for algorithm"""
    color_map = {
        'ucs': '#1f77b4',          # Blue
        'astar_haversine': '#2ca02c',   # Green
        'astar_euclidean': '#ff7f0e',   # Orange
        'astar_manhattan': '#d62728',   # Red
        'astar_min_graph': '#9467bd',   # Purple
        'astar_weighted': '#8c564b',    # Brown
        'greedy': '#e377c2',       # Pink
        'dfs': '#7f7f7f',          # Gray
    }
    return color_map.get(algo_key, '#808080')


def display_maps(result: dict, intermediate_cities: list = None):
    """Display Google Map with all algorithm paths - user can toggle visibility."""
    
    # 💡 GET THE API KEY FROM THE ENVIRONMENT
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    GOOGLE_ROADMAP_URL = f"https://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}&key={GOOGLE_MAPS_API_KEY}"

    if intermediate_cities is None:
        intermediate_cities = []
    
    st.info(f"📍 Intermediate cities: {', '.join(intermediate_cities) if intermediate_cities else 'None'}")

    # Build city coordinates from all algorithm results
    city_coordinates = {}
    for algo_key in result["results"]:
        algo_result = result["results"][algo_key]
        if algo_result.get("success"):
            path_coords = algo_result.get("path_coordinates", [])
            path_cities = algo_result.get("path", [])
            
            # Map each city name to its coordinates
            for city_name, coord in zip(path_cities, path_coords):
                if city_name not in city_coordinates:
                    city_coordinates[city_name] = (coord["lat"], coord["lon"])
    
    # Create map base with Google tiles
    m = folium.Map(
        location=[39.5, -98.0],
        zoom_start=4,
        tiles=None,
        attr="Google"
    )

    folium.TileLayer(
        tiles=GOOGLE_ROADMAP_URL,
        attr='Google Maps',
        name='Google Roadmap',
        overlay=False,
        control=True
    ).add_to(m)

    st.markdown("""
    Interactive map showing all algorithms. Adjust visibility using checkboxes below.
    """)
    
    # Get available algorithms from results
    available_algos = list(result["results"].keys())
    
   # Create color legend
    st.markdown("### Algorithm Color Map")
    
    algorithms_to_show = {}
    
    # Build legend text with colors
    for algo_key in available_algos:
        if algo_key in result["results"] and result["results"][algo_key].get("success"):
            display_name = _format_algo_name(algo_key)
            color = _get_algo_color(algo_key)
            # Display as simple colored text
            st.markdown(f"<span style='color: {color}; font-weight: bold; font-size: 16px;'>■</span> **{display_name}**", unsafe_allow_html=True)
            algorithms_to_show[algo_key] = True  # All algorithms visible by default
    # Optional: Show/Hide controls
    st.markdown("### Show/Hide Algorithms")
    
    col_width = 3
    cols = st.columns(col_width)
    
    for idx, algo_key in enumerate(available_algos):
        if algo_key in result["results"] and result["results"][algo_key].get("success"):
            display_name = _format_algo_name(algo_key)
            with cols[idx % col_width]:
                algorithms_to_show[algo_key] = st.checkbox(display_name, value=True, key=f"cb_{algo_key}")
    
    # Add each algorithm's path if checkbox is checked
    for algo_key, should_show in algorithms_to_show.items():
        if should_show and algo_key in result["results"]:
            algo_result = result["results"][algo_key]
            
            if algo_result.get("success"):
                color = _get_algo_color(algo_key)
                display_name = _format_algo_name(algo_key)
                coordinates = algo_result.get("path_coordinates", [])
                
                # Draw path line
                path_coords = [[c["lat"], c["lon"]] for c in coordinates]
                total_distance = algo_result.get("total_distance", 0)
                
                folium.PolyLine(
                    path_coords,
                    color=color,
                    weight=3,
                    opacity=0.8,
                    popup=f"{display_name}: {total_distance:.0f} mi"
                ).add_to(m)

                # Get cities in final path (excluding start/goal)
                path_cities = set(algo_result.get("path", [])[1:-1])
                
                # Get expanded states
                expanded_states = set(algo_result.get("expanded_states", []))
                
                # Plot intermediate cities for this algorithm
                for city in intermediate_cities:
                    if city in city_coordinates:
                        city_coords = city_coordinates[city]
                        
                        if city in path_cities:
                            # ✅ IN FINAL PATH - larger, colored dot
                            folium.CircleMarker(
                                location=city_coords,
                                radius=6,
                                color=color,
                                fill=True,
                                fillColor=color,
                                fillOpacity=0.8,
                                weight=2,
                                popup=f"{city} (in {display_name} path)",
                                tooltip=f"{city} - In {display_name} path"
                            ).add_to(m)
                        
                        elif city in expanded_states:
                            # 🔍 EXPLORED BUT NOT IN PATH - gray marker
                            folium.Marker(
                                location=city_coords,
                                icon=folium.Icon(
                                    color="gray",
                                    icon="search",
                                    prefix="fa"
                                ),
                                popup=f"{city} (explored by {display_name})",
                                tooltip=f"{city} - Explored by {display_name}"
                            ).add_to(m)
    
    # Add start and goal cities as circles
    # Use first successful algorithm for start/goal coordinates
    first_successful_algo = None
    for algo_key in result["results"]:
        if result["results"][algo_key].get("success"):
            first_successful_algo = result["results"][algo_key]
            break
    
    if first_successful_algo:
        start_coord = first_successful_algo.get("path_coordinates", [])[0]
        goal_coord = first_successful_algo.get("path_coordinates", [])[-1]
        path = first_successful_algo.get("path", [])
        
        # Start circle marker (blue)
        folium.CircleMarker(
            location=[start_coord["lat"], start_coord["lon"]],
            radius=12,
            popup=path[0],
            color="#4285F4",
            fill=True,
            fillColor="#4285F4",
            fillOpacity=0.9,
            weight=2,
            tooltip=f"Start: {path[0]}"
        ).add_to(m)
        
        # Goal circle marker (red)
        folium.CircleMarker(
            location=[goal_coord["lat"], goal_coord["lon"]],
            radius=12,
            popup=path[-1],
            color="#EA4335",
            fill=True,
            fillColor="#EA4335",
            fillOpacity=0.9,
            weight=2,
            tooltip=f"Goal: {path[-1]}"
        ).add_to(m)
    
    # Display map
    st_folium(m, width=1200, height=650)