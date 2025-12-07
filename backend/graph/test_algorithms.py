"""
Simple test script to verify the route optimization algorithms work.

Run this with: python test_algorithms.py

This will use the Google Maps API to fetch real city data.
Make sure GOOGLE_MAPS_API_KEY is set in .env or environment variables.
"""

from route_optimizer import RouteOptimizer
from city_graph import initialize_city_graph
import os


def print_result(result):
    """Pretty print algorithm results."""
    print(f"\n{'='*60}")
    print(f"Algorithm: {result.algorithm_name}")
    print(f"{'='*60}")
    
    if result.success:
        print(f"Path: {' → '.join(result.path)}")
        print(f"Total Distance: {result.path_cost:.2f} miles")
    else:
        print("Path: NO PATH FOUND")
        print("Total Distance: N/A")
    
    print(f"Nodes Expanded: {result.nodes_expanded}")
    print(f"Execution Time: {result.execution_time_ms:.2f} ms")


def main():

    # Initialize city graph with Google Maps API
    print("\nInitializing city graph...")
    try:
        city_graph = initialize_city_graph(use_cache=True)
        # print(f"✓ {city_graph}")
    except Exception as e:
        print(f"✗ Error initializing city graph: {e}")
        return
    
    print("\nAvailable cities:")
    cities = city_graph.get_all_cities()
  

    
    try:
        
        # Build dynamic network (same as backend does)
        print("\nBuilding dynamic network...")
        city_graph.build_dynamic_network("Potsdam, NY", "Austin, TX", num_intermediate=12)
        
        # Now run algorithms on the built network
        results = RouteOptimizer.run_all_algorithms("Potsdam, NY", "Austin, TX", city_graph)
        
        for algo in ["ucs", "astar", "greedy","dfs"]:
            print_result(results[algo])
        
        # Compare results
        print(f"\n{'='*60}")
        print("COMPARISON")
        print(f"{'='*60}")
        
        ucs_result = results["ucs"]
        astar_result = results["astar"]
        greedy_result = results["greedy"]
        dfs_result = results["dfs"]
        
        if ucs_result.success and astar_result.success:
            print(f"A* Nodes Expanded: {astar_result.nodes_expanded} "
                  f"(vs UCS: {ucs_result.nodes_expanded})")
            if ucs_result.nodes_expanded > 0:
                reduction = ((ucs_result.nodes_expanded - astar_result.nodes_expanded) / 
                           ucs_result.nodes_expanded) * 100
                print(f"  → A* saved {ucs_result.nodes_expanded - astar_result.nodes_expanded} "
                      f"node expansions ({reduction:.1f}% reduction)")
        
        if greedy_result.success and astar_result.success:
            if greedy_result.path_cost > astar_result.path_cost:
                excess = greedy_result.path_cost - astar_result.path_cost
                excess_pct = (excess / astar_result.path_cost) * 100
                print(f"Greedy Path: {greedy_result.path_cost:.2f} miles "
                      f"(vs A* optimal: {astar_result.path_cost:.2f} miles)")
                print(f"  → Greedy is suboptimal by {excess:.2f} miles ({excess_pct:.1f}% worse)")
            else:
                print(f"Greedy found optimal path!")
        if dfs_result.success:
            print(f"\nDFS Nodes Expanded: {dfs_result.nodes_expanded}")
            print(f"DFS Path: {dfs_result.path_cost:.2f} miles "
                  f"(vs A* optimal: {astar_result.path_cost:.2f} miles)")
            if dfs_result.path_cost > astar_result.path_cost:
                excess_pct = ((dfs_result.path_cost - astar_result.path_cost) / astar_result.path_cost) * 100
                print(f"  → DFS is suboptimal by {excess_pct:.1f}% worse")
    
    except Exception as e:
        print(f"Error in test 1: {e}")
    

if __name__ == "__main__":
    main()