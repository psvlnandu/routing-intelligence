"""
Input section component - handles user input for route selection.
"""
import streamlit as st
import requests
from utils import validate_cities, call_find_routes
from config import DEFAULT_FROM_CITY, DEFAULT_TO_CITY, API_URL


def display_input_section():
    """Display the input section in the sidebar for city selection."""
    st.sidebar.header("Configuration")
    
    # Display current API URL
    st.sidebar.info(f"API: {API_URL}")
    
    # City input fields
    col1, col2 = st.sidebar.columns(2)
    with col1:
        initial_city = st.text_input(
            "From:",
            value=DEFAULT_FROM_CITY,
            placeholder="Enter city name"
        )
    with col2:
        goal_city = st.text_input(
            "To:",
            value=DEFAULT_TO_CITY,
            placeholder="Enter city name"
        )
    
    # Find Routes button
    if st.sidebar.button("Find Routes", use_container_width=True, type="primary"):
        # Validate input
        is_valid, error_message = validate_cities(initial_city, goal_city)
        
        if not is_valid:
            st.error(error_message)
        else:
            try:
                with st.spinner("Building network and finding routes..."):
                    result = call_find_routes(initial_city, goal_city)
                
                st.session_state.last_result = result
                st.rerun()
            
            except requests.exceptions.ConnectionError as e:
                st.error(f"Cannot connect to backend. {str(e)}")
            except ValueError as e:
                st.error(f"API Error: {str(e)}")
            except Exception as e:
                st.error(f"Error: {str(e)}")