import streamlit as st
import folium
from streamlit_folium import st_folium
from config import ALGORITHM_NAMES, ALGORITHM_COLORS


def display_maps(result: dict):
    """
    Display maps for each algorithm showing the path found.
    
    Args:
        result: Dictionary containing results from backend API
    """
    st.divider()
    st.header("Visual Comparison")
    
    st.markdown("""
    Each map shows:
    - Colored dots: Cities visited by the algorithm
    - Colored line: The final path selected
    - Larger circle: Starting city
    - Flag marker: Destination city
    """)
    
    # Display maps for each algorithm
    map_cols = st.columns(4)
    
    algorithms = ["ucs", "astar", "greedy", "dfs"]
    
    for idx, algo_key in enumerate(algorithms):
        with map_cols[idx]:
            algo_result = result["results"][algo_key]
            algo_name = ALGORITHM_NAMES.get(algo_key, algo_key)
            
            st.markdown(f"### {algo_name}")
            
            if algo_result["success"]:
                map_obj = _create_algorithm_map(algo_result, algo_key)
                st_folium(map_obj, width=300, height=400)
            else:
                st.error("No path found")


def _create_algorithm_map(algo_result: dict, algo_key: str) -> folium.Map:
    """
    Create a Folium map for a single algorithm result.
    
    Args:
        algo_result: Result from a single algorithm
        algo_key: Algorithm key (ucs, astar, greedy, dfs)
    
    Returns:
        Folium Map object
    """
    # Create base map
    m = folium.Map(
        location=[39.5, -98.0],
        zoom_start=4,
        tiles="OpenStreetMap"
    )
    
    color = ALGORITHM_COLORS.get(algo_key, "#808080")
    path = algo_result["path"]
    coordinates = algo_result["path_coordinates"]
    
    # Add starting city (larger marker)
    if coordinates:
        start_lat = coordinates[0]["lat"]
        start_lon = coordinates[0]["lon"]
        folium.CircleMarker(
            location=[start_lat, start_lon],
            radius=10,
            popup=path[0],
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.9,
            weight=3,
            tooltip=f"Start: {path[0]}"
        ).add_to(m)
    
    # Add all cities on the path
    for city, coord in zip(path, coordinates):
        folium.CircleMarker(
            location=[coord["lat"], coord["lon"]],
            radius=6,
            popup=city,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.6,
            weight=2
        ).add_to(m)
    
    # Draw the path line
    path_coords = [[c["lat"], c["lon"]] for c in coordinates]
    folium.PolyLine(
        path_coords,
        color=color,
        weight=3,
        opacity=0.8
    ).add_to(m)
    
    # Add goal city marker
    if coordinates:
        goal_lat = coordinates[-1]["lat"]
        goal_lon = coordinates[-1]["lon"]
        folium.Marker(
            location=[goal_lat, goal_lon],
            popup=path[-1],
            icon=folium.Icon(color=color, icon="flag"),
            tooltip=f"Goal: {path[-1]}"
        ).add_to(m)
    
    return m