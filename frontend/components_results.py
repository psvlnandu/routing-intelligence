"""
Results display component - shows metrics and path information for each algorithm.
"""
import streamlit as st
from config import ALGORITHM_NAMES, ALGORITHM_COLORS


def display_results(result: dict):
    """
    Display results from all algorithms in a structured format.
    
    Args:
        result: Dictionary containing results from backend API
    """
    st.divider()
    st.header(f"{result['initial_city']} to {result['goal_city']}")
    
    # Create three columns for algorithm results
    col_ucs, col_astar, col_greedy, col_dfs = st.columns(4)
    
    algorithms = [
        ("ucs", col_ucs),
        ("astar", col_astar),
        ("greedy", col_greedy),
        ("dfs", col_dfs)
    ]
    
    results_data = {}
    
    for algo_key, col in algorithms:
        with col:
            _display_algorithm_result(result, algo_key, results_data)
    
    # Show comparisons
    st.divider()
    _display_comparisons(results_data)


def _display_algorithm_result(result: dict, algo_key: str, results_data: dict):
    """Display results for a single algorithm."""
    algo = result["results"][algo_key]
    algo_name = ALGORITHM_NAMES.get(algo_key, algo_key)
    
    st.markdown(f"### {algo_name}")
    
    if algo["success"]:
        st.success("Path found")
        st.metric("Distance", f"{algo['total_distance']:.0f} mi")
        st.metric("Nodes Expanded", algo['nodes_expanded'])
        st.metric("Time", f"{algo['execution_time_ms']:.2f} ms")
        
        st.markdown("**Route:**")
        path_text = " → ".join(algo['path'])
        st.code(path_text, language=None)
        
        results_data[algo_key] = algo
    else:
        st.error("No path found")


def _display_comparisons(results_data: dict):
    """Display algorithm comparisons."""
    if len(results_data) < 2:
        return
    
    st.header("Comparison")
    
    # A* vs UCS comparison
    if "astar" in results_data and "ucs" in results_data:
        ucs = results_data["ucs"]
        astar = results_data["astar"]
        
        savings = ucs['nodes_expanded'] - astar['nodes_expanded']
        savings_pct = (savings / ucs['nodes_expanded'] * 100) if ucs['nodes_expanded'] > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "A* Efficiency vs UCS",
                f"{savings} fewer nodes",
                f"-{savings_pct:.1f}%"
            )
        with col2:
            if astar['total_distance'] == ucs['total_distance']:
                st.metric("Path Quality", "Both optimal", "Equal")
    
    # Greedy optimality check
    if "greedy" in results_data and "astar" in results_data:
        greedy = results_data["greedy"]
        astar = results_data["astar"]
        
        if greedy['total_distance'] > astar['total_distance']:
            excess = greedy['total_distance'] - astar['total_distance']
            excess_pct = (excess / astar['total_distance']) * 100
            
            st.warning(
                f"Greedy Path: {excess_pct:.1f}% longer ({excess:.0f} miles) "
                f"than optimal A* solution"
            )
        else:
            st.success("Greedy found optimal path")
    
    # DFS analysis
    if "dfs" in results_data and "astar" in results_data:
        dfs = results_data["dfs"]
        astar = results_data["astar"]
        
        st.markdown("**DFS Analysis:**")
        if dfs['total_distance'] == astar['total_distance']:
            st.info("DFS found optimal path (but this is not guaranteed)")
        else:
            excess_pct = ((dfs['total_distance'] - astar['total_distance']) / astar['total_distance']) * 100
            st.warning(f"DFS path is {excess_pct:.1f}% suboptimal")