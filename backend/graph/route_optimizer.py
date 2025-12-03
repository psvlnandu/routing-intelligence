"""
Route Optimization Algorithms Runner

This module runs the three search algorithms (UCS, A*, Greedy) on a routing problem
and collects performance metrics:
- Path found
- Total distance
- Nodes expanded
- Execution time

Uses the search algorithms from the course's search.py module with instrumentation.
"""

import time
import sys
import os


# Import from professor's search framework
# Make sure search.py and utils.py are in the same directory
try:
    from search import (
        Node, 
        uniform_cost_search,
        astar_search,
        greedy_best_first_graph_search,
        depth_first_graph_search,
        InstrumentedProblem
    )
except ImportError as e:
    # print(f"Error: Could not import from search.py. Make sure search.py and utils.py are in this directory.")
    print(f"Error details: {e}")
    sys.exit(1)

from route_problem import RouteOptimizationProblem


class AlgorithmResult:
    """
    Contains the results of running a search algorithm.
    
    Attributes:
        algorithm_name: Name of the algorithm (e.g., "A*")
        path: List of city names from start to goal
        path_cost: Total distance traveled
        nodes_expanded: Number of nodes explored
        execution_time_ms: Time taken in milliseconds
        success: Whether goal was reached
    """
    def __init__(self, algorithm_name, path=None, path_cost=0, 
                 nodes_expanded=0, execution_time_ms=0, success=False):
        self.algorithm_name = algorithm_name
        self.path = path or []
        self.path_cost = path_cost
        self.nodes_expanded = nodes_expanded
        self.execution_time_ms = execution_time_ms
        self.success = success
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "algorithm": self.algorithm_name,
            "path": self.path,
            "total_distance": round(self.path_cost, 2),
            "nodes_expanded": self.nodes_expanded,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "success": self.success
        }


class RouteOptimizer:
    """
    Runs the three search algorithms on a routing problem using the professor's
    search.py functions with instrumentation.
    """
    
    @staticmethod
    def _extract_path(node):
        """
        Extract the path from a Node by traversing parent pointers.
        
        Args:
            node: A Node object from the search result
        
        Returns:
            List of state names (city names) from start to goal
        """
        if node is None:
            return []
        path = []
        current = node
        while current:
            path.append(current.state)
            current = current.parent
        return list(reversed(path))
    
    @staticmethod
    def uniform_cost_search(problem):
        """
        Uniform Cost Search using professor's implementation.
        
        Expands the node with the lowest path cost first.
        Guarantees finding the optimal path.
        """
        start_time = time.time()
        
        # Use professor's UCS function with instrumentation
        instrumented_problem = InstrumentedProblem(problem)
        result_node = uniform_cost_search(instrumented_problem, display=False)
        
        elapsed = (time.time() - start_time) * 1000
        
        if result_node:
            path = RouteOptimizer._extract_path(result_node)
            return AlgorithmResult(
                "UCS",
                path=path,
                path_cost=result_node.path_cost,
                nodes_expanded=instrumented_problem.states,
                execution_time_ms=elapsed,
                success=True
            )
        else:
            return AlgorithmResult(
                "UCS",
                nodes_expanded=instrumented_problem.states,
                execution_time_ms=elapsed,
                success=False
            )
    
    @staticmethod
    def astar_search(problem):
        """
        A* Search using professor's implementation.
        
        Expands nodes based on f(n) = g(n) + h(n) where g(n) is cost so far
        and h(n) is heuristic estimate.
        Guarantees finding the optimal path if heuristic is admissible.
        """
        start_time = time.time()
        
        # Use professor's A* function with instrumentation
        instrumented_problem = InstrumentedProblem(problem)
        result_node = astar_search(instrumented_problem, display=False)
        
        elapsed = (time.time() - start_time) * 1000
        
        if result_node:
            path = RouteOptimizer._extract_path(result_node)
            return AlgorithmResult(
                "A*",
                path=path,
                path_cost=result_node.path_cost,
                nodes_expanded=instrumented_problem.states,
                execution_time_ms=elapsed,
                success=True
            )
        else:
            return AlgorithmResult(
                "A*",
                nodes_expanded=instrumented_problem.states,
                execution_time_ms=elapsed,
                success=False
            )
    
    @staticmethod
    def greedy_best_first_search(problem):
        """
        Greedy Best-First Search using professor's implementation.
        
        Expands nodes based solely on h(n), the heuristic estimate.
        Faster than A* but does NOT guarantee optimal path.
        """
        start_time = time.time()
        
        # Use professor's Greedy function with instrumentation
        # greedy_best_first_graph_search is an alias for best_first_graph_search with f=h
        instrumented_problem = InstrumentedProblem(problem)
        result_node = greedy_best_first_graph_search(
            instrumented_problem, 
            lambda node: problem.h(node),
            display=False
        )
        
        elapsed = (time.time() - start_time) * 1000
        
        if result_node:
            path = RouteOptimizer._extract_path(result_node)
            return AlgorithmResult(
                "Greedy",
                path=path,
                path_cost=result_node.path_cost,
                nodes_expanded=instrumented_problem.states,
                execution_time_ms=elapsed,
                success=True
            )
        else:
            return AlgorithmResult(
                "Greedy",
                nodes_expanded=instrumented_problem.states,
                execution_time_ms=elapsed,
                success=False
            )
    
    @staticmethod
    def depth_first_search(problem):
        """
        Depth First Search using professor's implementation.
        
        Expands the deepest nodes first using a stack.
        Very fast but does NOT guarantee optimal path.
        May find very long paths.
        """
        start_time = time.time()
        
        # Use professor's DFS function with instrumentation
        instrumented_problem = InstrumentedProblem(problem)
        result_node = depth_first_graph_search(
            instrumented_problem
        )
        
        elapsed = (time.time() - start_time) * 1000
        
        if result_node:
            path = RouteOptimizer._extract_path(result_node)
            return AlgorithmResult(
                "DFS",
                path=path,
                path_cost=result_node.path_cost,
                nodes_expanded=instrumented_problem.states,
                execution_time_ms=elapsed,
                success=True
            )
        else:
            return AlgorithmResult(
                "DFS",
                nodes_expanded=instrumented_problem.states,
                execution_time_ms=elapsed,
                success=False
            )
    @staticmethod
    def run_all_algorithms(initial_city, goal_city, city_graph):
        """
        Run all three algorithms on the same problem and return results.
        
        Args:
            initial_city: Starting city name (string)
            goal_city: Destination city name (string)
            city_graph: Initialized CityGraph object
        
        Returns:
            Dictionary with keys "ucs", "astar", "greedy" containing AlgorithmResult objects
        """
        problem = RouteOptimizationProblem(initial_city, goal_city, city_graph)
        
        results = {
            "ucs": RouteOptimizer.uniform_cost_search(problem),
            "astar": RouteOptimizer.astar_search(problem),
            "greedy": RouteOptimizer.greedy_best_first_search(problem),
            "dfs": RouteOptimizer.depth_first_search(problem),
        }
        
        return results