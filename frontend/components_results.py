"""
Results display component - Shows algorithm performance metrics and comparisons.
"""
import streamlit as st
import pandas as pd


def display_results(result: dict):
    """
    Display results from all algorithms in a structured format using accordions.
    
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
        with st.expander("▼ Uninformed Search", expanded=True):
            for algo_key in ucs_results:
                _display_algorithm_result_compact(result, algo_key)
    
    # Display A* variants
    if astar_results:
        with st.expander("▼ A* Search (Informed - Different Heuristics)", expanded=True):
            for algo_key in astar_results:
                _display_algorithm_result_compact(result, algo_key)
    
    # Display Greedy
    if greedy_results:
        with st.expander("▼ Greedy Search", expanded=False):
            for algo_key in greedy_results:
                _display_algorithm_result_compact(result, algo_key)
    
    # Display DFS
    if dfs_results:
        with st.expander("▼ Depth-First Search", expanded=False):
            for algo_key in dfs_results:
                _display_algorithm_result_compact(result, algo_key)
    
    # Show comparisons
    st.divider()
    _display_comparisons(result["results"])


def _display_algorithm_result_compact(result: dict, algo_key: str):
    """
    Display individual algorithm result in compact format (for accordions).
    
    Args:
        result: Full result dictionary from backend
        algo_key: Key to access algorithm result (e.g., 'ucs', 'astar_haversine')
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
    path = algo_result.get("path", [])
    
    # Format algo name for display
    display_name = _format_algo_name(algo_key)
    
    # Display algorithm info in columns
    col1, col2, col3, col4, col5 = st.columns([2, 1.2, 1.2, 1.2, 1.2])
    
    with col1:
        st.markdown(f"**{display_name}**")
    
    with col2:
        st.write(f"📍 **{distance:.0f} mi**")
    
    with col3:
        st.write(f"🔍 **{nodes_expanded}**")
    
    with col4:
        st.write(f"⏱️ **{execution_time:.1f} ms**")
    
    with col5:
        st.write(f"🛣️ **{path_length}**")
    
    # Show route inline
    if path:
        path_str = " → ".join(path)
        st.caption(f"📋 **Route:** {path_str}")
    
    st.divider()


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
    
    st.header("📊 Algorithm Comparison")
    
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
    st.markdown("### 📈 Analysis")
    
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
        st.markdown("### 📊 Heuristic Impact (vs UCS)")
        ucs_nodes = df.loc[ucs_algo, "Nodes Expanded"]
        
        # Calculate efficiency improvements
        efficiency_data = {}
        for algo_name in astar_algos:
            astar_nodes = df.loc[algo_name, "Nodes Expanded"]
            reduction = ((ucs_nodes - astar_nodes) / ucs_nodes) * 100
            efficiency_data[algo_name] = max(0, reduction)  # Ensure non-negative
        
        # Sort by efficiency
        sorted_efficiency = sorted(efficiency_data.items(), key=lambda x: x[1], reverse=True)
        
        # Create two-column layout
        col_chart, col_rank = st.columns([2, 1])
        
        with col_chart:
            # Prepare data for horizontal bar chart
            efficiency_df = pd.DataFrame(sorted_efficiency, columns=['Heuristic', 'Reduction %'])
            
            # Use st.bar_chart for simple visualization
            st.bar_chart(
                efficiency_df.set_index('Heuristic')['Reduction %'],
                use_container_width=True,
                height=300
            )
        
        with col_rank:
            st.markdown("**Efficiency Ranking:**")
            for idx, (algo_name, reduction) in enumerate(sorted_efficiency, 1):
                if idx == 1:
                    emoji = "🥇"
                elif idx == 2:
                    emoji = "🥈"
                elif idx == 3:
                    emoji = "🥉"
                else:
                    emoji = "  "
                
                st.markdown(f"{emoji} {algo_name}\n**{reduction:.1f}%**")


def display_no_results():
    """Display message when no results are available."""
    st.info("🔍 Enter two cities and click 'Find Routes' to see algorithm comparisons")