"""
Utility functions for communicating with the Route Optimization backend API.
"""
import requests
import streamlit as st
from config import API_URL, API_TIMEOUT


def call_find_routes(initial_city: str, goal_city: str) -> dict:
    """
    Call the backend API to find routes between two cities.
    
    Args:
        initial_city: Starting city name
        goal_city: Destination city name
    
    Returns:
        Dictionary containing route results from all algorithms
    
    Raises:
        requests.exceptions.ConnectionError: If backend is unreachable
        ValueError: If API returns an error
    """
    try:
        response = requests.post(
            f"{API_URL}/routes",
            json={
                "initial_city": initial_city.strip(),
                "goal_city": goal_city.strip()
            },
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            raise ValueError(f"API Error {response.status_code}: {error_detail}")
    
    except requests.exceptions.ConnectionError:
        raise requests.exceptions.ConnectionError(
            f"Cannot connect to backend at {API_URL}. Make sure the backend service is running."
        )
    except requests.exceptions.Timeout:
        raise requests.exceptions.Timeout(
            f"Request timed out. The backend took longer than {API_TIMEOUT} seconds to respond."
        )
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


def validate_cities(initial_city: str, goal_city: str) -> tuple[bool, str]:
    """
    Validate user input for cities.
    
    Args:
        initial_city: Starting city name
        goal_city: Destination city name
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not initial_city or not initial_city.strip():
        return False, "Please enter a starting city"
    
    if not goal_city or not goal_city.strip():
        return False, "Please enter a destination city"
    
    if initial_city.strip() == goal_city.strip():
        return False, "Starting and destination cities must be different"
    
    return True, ""