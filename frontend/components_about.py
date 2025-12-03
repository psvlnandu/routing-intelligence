"""
About page component - displays project information and algorithm explanations.
"""
import streamlit as st


def display_about():
    """Display the about page with project information."""
    st.header("About This Project")
    
    st.markdown("""
    ### AI Techniques Demonstrated
    
    1. **Graph Search**: Finding paths in networks using uninformed and informed search
    2. **Heuristics**: Using domain knowledge (straight-line distance) to guide search
    3. **Algorithm Analysis**: Comparing efficiency, optimality, and node expansion
    4. **Empirical Evaluation**: Measuring performance on real geographic networks
    5. **API Integration**: Using Google Maps for real geographic data
    
    ### Algorithm Comparison
    
    #### UCS (Uniform Cost Search)
    - Expands nodes with lowest cost first
    - Guarantees optimal path
    - Explores many nodes (inefficient)
    - Uses: baseline for comparison
    
    #### A* Search
    - Expands nodes based on f(n) = g(n) + h(n)
    - Uses heuristic: straight-line distance
    - Guarantees optimal path
    - More efficient than UCS (fewer nodes expanded)
    - Uses: Google Maps, real-world routing
    
    #### Greedy Best-First
    - Expands nodes only based on heuristic h(n)
    - Fastest exploration
    - Does not guarantee optimal path
    - May find suboptimal solutions
    - Uses: speed-critical applications
    
    #### Depth-First Search
    - Expands deepest nodes first
    - Very fast exploration
    - Does not guarantee optimal path
    - May find very long paths
    - Uses: comparison of search strategies
    
    ### Why A* Wins in Real-World Applications
    
    A* provides the best balance:
    - Optimal solution like UCS
    - Efficient exploration like Greedy
    - Practical for routing systems (e.g., Google Maps)
    - Heuristic guides search toward goal
    
    ### Project Details
    
    **Backend**: FastAPI with Python search framework  
    **Frontend**: Streamlit with Folium maps  
    **Data**: Google Maps API (real city coordinates and distances)  
    **Algorithms**: Professor's search.py implementation  
    
    **Author**: Poorna  
    **Course**: Artificial Intelligence  
    **Institution**: Clarkson University  
    """)