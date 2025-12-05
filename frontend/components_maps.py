"""
Map display component - Google Maps with toggleable algorithm paths.
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import os
from config import ALGORITHM_COLORS, ALGORITHM_NAMES


def display_maps(result: dict):
    """Display Google Map with all algorithm paths - user can toggle visibility."""
    
    # 💡 GET THE API KEY FROM THE ENVIRONMENT
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    GOOGLE_ROADMAP_URL = f"https://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}&key={GOOGLE_MAPS_API_KEY}"

    # Create map base with no tiles
    m = folium.Map(
        location=[39.5, -98.0],
        zoom_start=4,
        tiles=None, # Set to None, we'll add the layer manually
        attr="Google"
    )

   
    folium.TileLayer(
        tiles=GOOGLE_ROADMAP_URL,
        attr='Google Maps',
        name='Google Roadmap',
        overlay=False,
        control=True
    ).add_to(m)

    # ... (rest of path and marker code remains the same) ...
    
   
    st.markdown("""
    Interactive map showing all four algorithms. Use checkboxes to show/hide paths.
    """)
    
    # Checkboxes to toggle algorithm visibility
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        show_ucs = st.checkbox("UCS (Dijkstra)", value=True)
    with col2:
        show_astar = st.checkbox("A* Search", value=True)
    with col3:
        show_greedy = st.checkbox("Greedy Best-First", value=True)
    with col4:
        show_dfs = st.checkbox("Depth-First Search", value=True)
    
    algorithms_to_show = {
        "ucs": show_ucs,
        "astar": show_astar,
        "greedy": show_greedy,
        "dfs": show_dfs
    }

    
    # Add each algorithm's path if checkbox is checked
    for algo_key, should_show in algorithms_to_show.items():
        if should_show:
            algo_result = result["results"][algo_key]
            
            if algo_result["success"]:
                color = ALGORITHM_COLORS.get(algo_key, "#808080")
                coordinates = algo_result["path_coordinates"]
                
                # Draw path line
                path_coords = [[c["lat"], c["lon"]] for c in coordinates]
                folium.PolyLine(
                    path_coords,
                    color=color,
                    weight=3,
                    opacity=0.8,
                    popup=f"{ALGORITHM_NAMES[algo_key]}: {algo_result['total_distance']:.0f} mi"
                ).add_to(m)
    
    # Add start and goal cities as circles (like Google Maps)
    first_algo = result["results"]["ucs"]
    if first_algo["success"]:
        start_coord = first_algo["path_coordinates"][0]
        goal_coord = first_algo["path_coordinates"][-1]
        
        # Start circle marker (larger, blue)
        folium.CircleMarker(
            location=[start_coord["lat"], start_coord["lon"]],
            radius=12,
            popup=first_algo["path"][0],
            color="#4285F4",
            fill=True,
            fillColor="#4285F4",
            fillOpacity=0.9,
            weight=2,
            tooltip=f"Start: {first_algo['path'][0]}"
        ).add_to(m)
        
        # Goal circle marker (larger, red)
        folium.CircleMarker(
            location=[goal_coord["lat"], goal_coord["lon"]],
            radius=12,
            popup=first_algo["path"][-1],
            color="#EA4335",
            fill=True,
            fillColor="#EA4335",
            fillOpacity=0.9,
            weight=2,
            tooltip=f"Goal: {first_algo['path'][-1]}"
        ).add_to(m)
    
    # Display map
    st_folium(m, width=1200, height=650)