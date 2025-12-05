"""
Route Optimization Visualizer - Streamlit Frontend

A web application that visualizes how different pathfinding algorithms
(UCS, A*, Greedy, DFS) explore search spaces to find routes between cities.

Uses Google Maps API for real geographic data and the professor's search.py framework.

Run with: streamlit run app.py
"""

import sys
import os

# Add frontend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from config import PAGE_TITLE, PAGE_ICON, LAYOUT, INITIAL_SIDEBAR_STATE
from components_header import display_header
from components_input import display_input_section
from components_results import display_results
from components_maps import display_maps
from components_about import display_about

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================

st.markdown("""
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point."""
    
    # Display header
    display_header()
    
    # Display input section in sidebar
    display_input_section()
    
    # Display results if available
    if "last_result" in st.session_state:
        result = st.session_state.last_result
        
        # Show results table
        display_results(result)
        
        # Show maps visualization
        display_maps(result)
    
    # Sidebar information
    with st.sidebar:
        st.divider()
        st.markdown("""
        ### Project Information
        
        **Author**: Poorna  
        **Course**: Artificial Intelligence  
        **Institution**: Clarkson University  
        
        This application demonstrates how different search algorithms explore
        the same problem space differently, comparing their efficiency and optimality.
        """)


if __name__ == "__main__":
    main()