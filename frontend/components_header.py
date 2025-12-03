"""
Header component - displays project title and description.
"""
import streamlit as st


def display_header():
    """Display the application header with title and description."""
    st.title("Route Optimization: AI Algorithm Comparison")
    
    st.markdown("""
    This application compares three pathfinding algorithms on real geographic data 
    from the United States using the Google Maps API.
    
    **Algorithms Compared:**
    - **UCS (Uniform Cost Search)**: Guarantees optimal path but explores many nodes
    - **A* Search**: Finds optimal path efficiently using a heuristic
    - **Greedy Best-First**: Fastest but may find suboptimal paths
    - **Depth-First Search**: Explores deeply, very fast but doesn't guarantee optimality
    
    Enter any two US locations to see how each algorithm explores the search space differently.
    """)
    
    st.divider()