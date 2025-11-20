"""
Simple test script to verify the route optimization algorithms work.

Run this with: python test_algorithms.py
"""

from route_optimizer import RouteOptimizer
from city_graph import city_graph


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
    """Test the algorithms on various routes."""
    
    print("\n" + "="*60)
    print("ROUTE OPTIMIZATION - ALGORITHM COMPARISON")
    print("="*60)
    
    print("\nAvailable cities:")
    cities = city_graph.get_all_cities()
    for i, city in enumerate(sorted(cities), 1):
        print(f"  {i:2d}. {city}")
    
    # Test route 1: Buffalo to NYC
    print("\n" + "="*80)
    print("TEST 1: Buffalo → NYC")
    print("="*80)
    
    results = RouteOptimizer.run_all_algorithms("Buffalo", "NYC")
    
    for algo in ["ucs", "astar", "greedy"]:
        print_result(results[algo])
    
    # Compare results
    print(f"\n{'='*60}")
    print("COMPARISON")
    print(f"{'='*60}")
    
    ucs_result = results["ucs"]
    astar_result = results["astar"]
    greedy_result = results["greedy"]
    
    if ucs_result.success and astar_result.success:
        print(f"A* Nodes Expanded: {astar_result.nodes_expanded} "
              f"(vs UCS: {ucs_result.nodes_expanded})")
        print(f"  → A* saved {ucs_result.nodes_expanded - astar_result.nodes_expanded} "
              f"node expansions "
              f"({((1 - astar_result.nodes_expanded/ucs_result.nodes_expanded)*100):.1f}% reduction)")
    
    if greedy_result.success and astar_result.success:
        if greedy_result.path_cost > astar_result.path_cost:
            print(f"Greedy Path: {greedy_result.path_cost:.2f} miles "
                  f"(vs A* optimal: {astar_result.path_cost:.2f} miles)")
            print(f"  → Greedy is suboptimal by {greedy_result.path_cost - astar_result.path_cost:.2f} miles")
        else:
            print(f"Greedy found optimal path!")
    
    # Test route 2: Rochester to Albany
    print("\n" + "="*80)
    print("TEST 2: Rochester → Albany")
    print("="*80)
    
    results2 = RouteOptimizer.run_all_algorithms("Rochester", "Albany")
    
    for algo in ["ucs", "astar", "greedy"]:
        print_result(results2[algo])
    
    print("\n" + "="*60)
    print("✓ All tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()