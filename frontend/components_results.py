"""
Results display component - Shows algorithm performance metrics and comparisons.
"""
import streamlit as st
import pandas as pd


def display_results(result: dict):
    """
    Display results from all algorithms in a structured format.
    
    Args:
        result: Dictionary containing results from backend API
    """
    st.divider()
    st.header(f"{result['initial_city']} to {result['goal_city']}")
    
    # Get available algorithms from results
    available_algos = list(result["results"].keys())
    
    # Separate by type
    ucs_results = [a for a in available_algos if 'ucs' in a]
    astar_results = [a for a in available_algos if 'astar' in a]
    greedy_results = [a for a in available_algos if 'greedy' in a]
    dfs_results = [a for a in available_algos if 'dfs' in a]
    
    # Display UCS
    if ucs_results:
        st.subheader("Uninformed Search")
        cols = st.columns(len(ucs_results))
        results_data = {}
        for idx, algo_key in enumerate(ucs_results):
            with cols[idx]:
                _display_algorithm_result(result, algo_key, results_data)
    
    # Display A* variants
    if astar_results:
        st.subheader("A* Search (Informed - Different Heuristics)")
        cols = st.columns(min(3, len(astar_results)))
        results_data = {}
        for idx, algo_key in enumerate(astar_results):
            with cols[idx % len(cols)]:
                _display_algorithm_result(result, algo_key, results_data)
    
    # Display Greedy
    if greedy_results:
        st.subheader("Greedy Search")
        cols = st.columns(len(greedy_results))
        results_data = {}
        for idx, algo_key in enumerate(greedy_results):
            with cols[idx]:
                _display_algorithm_result(result, algo_key, results_data)
    
    # Display DFS
    if dfs_results:
        st.subheader("Depth-First Search")
        cols = st.columns(len(dfs_results))
        results_data = {}
        for idx, algo_key in enumerate(dfs_results):
            with cols[idx]:
                _display_algorithm_result(result, algo_key, results_data)
    
    # Show comparisons
    st.divider()
    _display_comparisons(result["results"])


def _display_algorithm_result(result: dict, algo_key: str, results_data: dict):
    """
    Display individual algorithm result card.
    
    Args:
        result: Full result dictionary from backend
        algo_key: Key to access algorithm result (e.g., 'ucs', 'astar_haversine')
        results_data: Dictionary to store results for comparison
    """
    if algo_key not in result["results"]:
        st.warning(f"❌ {algo_key} - No results")
        return
    
    algo_result = result["results"][algo_key]
    
    if not algo_result.get("success", False):
        st.error(f"❌ {algo_key} - Failed")
        return
    
    # Extract data
    distance = algo_result.get("total_distance", 0)
    nodes_expanded = algo_result.get("nodes_expanded", 0)
    execution_time = algo_result.get("execution_time_ms", 0)
    path_length = len(algo_result.get("path", []))
    
    # Format algo name for display
    display_name = _format_algo_name(algo_key)
    
    # Store for comparison
    results_data[display_name] = {
        "Distance (mi)": round(distance, 1),
        "Nodes Expanded": nodes_expanded,
        "Execution Time (ms)": round(execution_time, 2),
        "Path Length": path_length,
    }
    
    # Display card
    with st.container():
        st.markdown(f"### {display_name}")
        
        # Metrics row
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "📍 Distance",
                f"{distance:.0f} mi",
                help="Total miles driven"
            )
            st.metric(
                "🔍 Nodes",
                f"{nodes_expanded}",
                help="Number of cities examined"
            )
        
        with col2:
            st.metric(
                "⏱️ Time",
                f"{execution_time:.1f} ms",
                help="Algorithm execution time"
            )
            st.metric(
                "🛣️ Cities",
                f"{path_length}",
                help="Number of cities in final path"
            )
        
        # Path display
        path = algo_result.get("path", [])
        if path:
            with st.expander("📋 Route"):
                path_str = " → ".join(path)
                st.text(path_str)


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


def _display_comparisons(all_results: dict):
    """
    Display comparison table and analysis of all algorithms.
    
    Args:
        all_results: Dictionary with results from all algorithms
    """
    if not all_results:
        return
    
    st.header("Algorithm Comparison")
    
    # Build comparison data
    comparison_data = {}
    for algo_key, algo_result in all_results.items():
        if algo_result.get("success", False):
            display_name = _format_algo_name(algo_key)
            comparison_data[display_name] = {
                "Distance (mi)": round(algo_result.get("total_distance", 0), 1),
                "Nodes Expanded": algo_result.get("nodes_expanded", 0),
                "Execution Time (ms)": round(algo_result.get("execution_time_ms", 0), 2),
                "Path Length": len(algo_result.get("path", [])),
            }
    
    if not comparison_data:
        st.warning("No successful results to compare")
        return
    
    # Create comparison DataFrame
    df = pd.DataFrame(comparison_data).T
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Distance (mi)": st.column_config.NumberColumn(format="%.1f mi"),
            "Nodes Expanded": st.column_config.NumberColumn(format="%d"),
            "Execution Time (ms)": st.column_config.NumberColumn(format="%.2f ms"),
            "Path Length": st.column_config.NumberColumn(format="%d"),
        }
    )
    
    # Analysis
    st.markdown("### Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        best_distance_algo = df["Distance (mi)"].idxmin()
        best_distance_value = df["Distance (mi)"].min()
        st.info(f"**Shortest Route**\n{best_distance_algo}\n{best_distance_value:.0f} mi")
    
    with col2:
        best_nodes_algo = df["Nodes Expanded"].idxmin()
        best_nodes_value = df["Nodes Expanded"].min()
        st.success(f"**Most Efficient**\n{best_nodes_algo}\n{best_nodes_value} nodes")
    
    with col3:
        fastest_algo = df["Execution Time (ms)"].idxmin()
        fastest_value = df["Execution Time (ms)"].min()
        st.warning(f"**Fastest**\n{fastest_algo}\n{fastest_value:.2f} ms")
    
    # Heuristic effectiveness (A* variants only)
    astar_algos = [algo for algo in df.index if 'A*' in algo]
    if len(astar_algos) > 1:
        astar_df = df.loc[astar_algos]
        astar_df_sorted = astar_df.sort_values("Nodes Expanded")
        
        best_heuristic = astar_df["Nodes Expanded"].idxmin()
        st.success(f"🏆 **Best heuristic**: {best_heuristic}")
    
    # UCS vs Heuristic comparison
    ucs_algo = next((a for a in df.index if 'UCS' in a), None)
    if ucs_algo and len(astar_algos) > 0:
        st.markdown("### Heuristic Impact (vs UCS)")
        ucs_nodes = df.loc[ucs_algo, "Nodes Expanded"]
        
        for algo_name in astar_algos:
            astar_nodes = df.loc[algo_name, "Nodes Expanded"]
            reduction = ((ucs_nodes - astar_nodes) / ucs_nodes) * 100
            st.markdown(f"- {algo_name}: **{reduction:.1f}%** fewer nodes explored")


def display_no_results():
    """Display message when no results are available."""
    st.info("🔍 Enter two cities and click 'Find Routes' to see algorithm comparisons")