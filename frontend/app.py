"""
Route Optimization Visualizer - Streamlit Frontend

A web app that visualizes how UCS, A*, and Greedy Best-First search
explore different regions of New York State to find optimal routes.

Uses Google Maps API for real city data.

Run with: streamlit run app.py
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import json
from typing import Dict, List

# Page configuration
st.set_page_config(
    page_title="Route Optimization: Algorithm Comparison",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .algorithm-header {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .path-text {
        font-family: monospace;
        font-size: 12px;
        word-break: break-all;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🗺️ Route Optimization: AI Algorithm Comparison")

st.markdown("""
This project compares three pathfinding algorithms on **real NY State cities** (powered by Google Maps API):

- **UCS (Uniform Cost Search)**: Like Dijkstra's algorithm. Guarantees optimal path.
- **A* Search**: Uses a heuristic (straight-line distance) to guide search. Optimal AND more efficient.
- **Greedy Best-First**: Only uses heuristic. Fastest but may find suboptimal paths.

**Watch how each algorithm explores a different portion of the map!**
""")

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")

# API endpoint
api_url = st.sidebar.text_input(
    "API URL",
    value="http://localhost:8000",
    help="FastAPI backend URL"
)

# Get list of cities
@st.cache_data
def get_cities(api_url):
    try:
        response = requests.get(f"{api_url}/cities", timeout=5)
        if response.status_code == 200:
            return sorted(response.json()["cities"])
    except Exception as e:
        st.sidebar.error(f"Cannot connect to API: {e}")
        return []

cities = get_cities(api_url)

if not cities:
    st.error("❌ Cannot connect to backend.")
    st.info("""
    **How to fix:**
    
    1. Make sure you have Google Maps API key set up:
       - Read: `GOOGLE_MAPS_SETUP.md`
       - Copy `.env.example` to `.env`
       - Add your API key to `.env`
    
    2. Start the backend in a terminal:
       ```
       pip install -r requirements.txt
       python main.py
       ```
    
    3. Then run this Streamlit app:
       ```
       streamlit run app.py
       ```
    """)
    st.stop()

# City selection
col1, col2 = st.sidebar.columns(2)
with col1:
    initial_city = st.selectbox(
        "📍 From:",
        cities,
        index=0,
        key="initial"
    )

with col2:
    goal_city = st.selectbox(
        "📍 To:",
        cities,
        index=min(10, len(cities)-1),
        key="goal"
    )

# Find routes button
if st.sidebar.button("🔍 Find Routes", use_container_width=True, type="primary"):
    if initial_city == goal_city:
        st.error("Initial and goal cities must be different!")
    else:
        # Call API
        try:
            with st.spinner("Running algorithms..."):
                response = requests.post(
                    f"{api_url}/routes",
                    json={
                        "initial_city": initial_city,
                        "goal_city": goal_city
                    },
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.last_result = data
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                st.error(f"API Error: {error_detail}")
        
        except requests.exceptions.ConnectionError:
            st.error("""
            ❌ Cannot connect to backend. 
            
            Make sure to run in terminal:
            ```
            python main.py
            ```
            """)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display results if available
if "last_result" in st.session_state:
    result = st.session_state.last_result
    
    st.divider()
    st.header(f"📍 {result['initial_city']} → {result['goal_city']}")
    
    # Create three columns for the three algorithms
    col_ucs, col_astar, col_greedy = st.columns(3)
    
    algorithms = {
        "UCS": ("col_ucs", "🔵"),
        "A*": ("col_astar", "🔴"),
        "Greedy": ("col_greedy", "🟢")
    }
    
    algorithm_data = {}
    
    # --- UCS COLUMN ---
    with col_ucs:
        st.markdown("### 🔵 UCS (Dijkstra)")
        ucs = result["results"]["ucs"]
        
        if ucs["success"]:
            st.success(f"✓ Path found")
            st.metric("Total Distance", f"{ucs['total_distance']:.0f} miles", delta=None)
            st.metric("Nodes Expanded", ucs['nodes_expanded'])
            st.metric("Time", f"{ucs['execution_time_ms']:.2f} ms")
            
            st.markdown("**Route:**")
            st.markdown(
                '<div class="path-text">' + ' → '.join(ucs['path']) + '</div>',
                unsafe_allow_html=True
            )
            
            algorithm_data["UCS"] = ucs
        else:
            st.error("No path found")
    
    # --- A* COLUMN ---
    with col_astar:
        st.markdown("### 🔴 A* Search")
        astar = result["results"]["astar"]
        
        if astar["success"]:
            st.success(f"✓ Path found")
            st.metric("Total Distance", f"{astar['total_distance']:.0f} miles", delta=None)
            st.metric("Nodes Expanded", astar['nodes_expanded'])
            st.metric("Time", f"{astar['execution_time_ms']:.2f} ms")
            
            st.markdown("**Route:**")
            st.markdown(
                '<div class="path-text">' + ' → '.join(astar['path']) + '</div>',
                unsafe_allow_html=True
            )
            
            algorithm_data["A*"] = astar
            
            # Show comparison with UCS
            if ucs["success"]:
                st.divider()
                st.markdown("**vs UCS Comparison:**")
                savings = ucs['nodes_expanded'] - astar['nodes_expanded']
                savings_pct = (savings / ucs['nodes_expanded']) * 100 if ucs['nodes_expanded'] > 0 else 0
                st.info(f"A* expanded **{savings} fewer nodes** ({savings_pct:.1f}% reduction)")
        else:
            st.error("No path found")
    
    # --- GREEDY COLUMN ---
    with col_greedy:
        st.markdown("### 🟢 Greedy Best-First")
        greedy = result["results"]["greedy"]
        
        if greedy["success"]:
            st.success(f"✓ Path found")
            st.metric("Total Distance", f"{greedy['total_distance']:.0f} miles", delta=None)
            st.metric("Nodes Expanded", greedy['nodes_expanded'])
            st.metric("Time", f"{greedy['execution_time_ms']:.2f} ms")
            
            st.markdown("**Route:**")
            st.markdown(
                '<div class="path-text">' + ' → '.join(greedy['path']) + '</div>',
                unsafe_allow_html=True
            )
            
            algorithm_data["Greedy"] = greedy
            
            # Show if suboptimal
            if astar["success"] and greedy['total_distance'] > astar['total_distance']:
                st.divider()
                st.markdown("**Optimality:**")
                excess = greedy['total_distance'] - astar['total_distance']
                excess_pct = (excess / astar['total_distance']) * 100
                st.warning(
                    f"Suboptimal by **{excess:.0f} miles** ({excess_pct:.1f}% worse than A*)"
                )
        else:
            st.error("No path found")
    
    # --- MAPS VISUALIZATION ---
    st.divider()
    st.header("🗺️ Visual Comparison")
    st.markdown("""
    Each map shows:
    - **Colored dots**: Cities the algorithm visited (explored)
    - **Colored line**: Final path chosen
    - Larger circle = starting city, Smaller circle = goal city
    """)
    
    map_cols = st.columns(3)
    
    # Color scheme for algorithms
    colors = {
        "UCS": "blue",
        "A*": "red",
        "Greedy": "green"
    }
    
    for idx, (algo_name, algo_key) in enumerate([("UCS", "ucs"), ("A*", "astar"), ("Greedy", "greedy")]):
        with map_cols[idx]:
            st.markdown(f"### {algo_name}")
            
            algo_result = result["results"][algo_key]
            
            if algo_result["success"]:
                # Create map centered on NY State
                m = folium.Map(
                    location=[42.5, -77.5],
                    zoom_start=7,
                    tiles="OpenStreetMap"
                )
                
                color = colors[algo_name]
                
                # Add starting city (larger circle)
                start_lat, start_lon = algo_result["path_coordinates"][0]["lat"], algo_result["path_coordinates"][0]["lon"]
                folium.CircleMarker(
                    location=[start_lat, start_lon],
                    radius=10,
                    popup=algo_result["path"][0],
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.9,
                    weight=3,
                    tooltip=f"Start: {algo_result['path'][0]}"
                ).add_to(m)
                
                # Add all explored cities as small circles
                for city in algo_result["path"]:
                    lat, lon = None, None
                    for coord_entry in algo_result["path_coordinates"]:
                        if algo_result["path"][algo_result["path_coordinates"].index(coord_entry)] == city:
                            lat, lon = coord_entry["lat"], coord_entry["lon"]
                            break
                    
                    if lat and lon:
                        folium.CircleMarker(
                            location=[lat, lon],
                            radius=6,
                            popup=city,
                            color=color,
                            fill=True,
                            fillColor=color,
                            fillOpacity=0.6,
                            weight=2
                        ).add_to(m)
                
                # Add the path line
                path_coords = [[coord["lat"], coord["lon"]] for coord in algo_result["path_coordinates"]]
                folium.PolyLine(
                    path_coords,
                    color=color,
                    weight=3,
                    opacity=0.8,
                    popup=f"{algo_name} Path"
                ).add_to(m)
                
                # Add goal city (marked with marker)
                goal_lat, goal_lon = algo_result["path_coordinates"][-1]["lat"], algo_result["path_coordinates"][-1]["lon"]
                folium.Marker(
                    location=[goal_lat, goal_lon],
                    popup=algo_result["path"][-1],
                    icon=folium.Icon(color=color, icon="flag"),
                    tooltip=f"Goal: {algo_result['path'][-1]}"
                ).add_to(m)
                
                # Display map
                st_folium(m, width=350, height=450)
            else:
                st.error("No path found")

# Information section
with st.sidebar:
    st.divider()
    st.header("ℹ️ About This Project")
    st.markdown("""
    **AI Techniques Demonstrated:**
    
    1. **Graph Search**: Finding paths in networks
    2. **Heuristics**: Using domain knowledge (straight-line distance) to guide search
    3. **Algorithm Efficiency**: Trading optimality for speed
    4. **Empirical Analysis**: Measuring and comparing algorithm performance
    5. **API Integration**: Using Google Maps for real geographic data
    
    **Why A* Wins:**
    - Uses heuristic to prioritize promising paths
    - Expands fewer nodes than Dijkstra (UCS)
    - Still guarantees optimal solution
    - Perfect balance of efficiency and correctness
    """)
    
    st.divider()
    st.markdown("""
    **Project by**: Poorna  
    **Course**: Artificial Intelligence  
    **Institution**: Clarkson University
    """)