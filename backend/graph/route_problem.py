"""
Route Optimization Problem

This module defines the RouteOptimizationProblem class which extends the abstract
Problem class from the course framework. It represents the problem of finding the
shortest path between two cities in New York State.

A STATE in this problem is represented as a single string (the current city name).

The problem:
- Initial state: Starting city (string)
- Goal state: Destination city (string)
- Actions: Move to any neighboring city
- Path cost: Sum of driving distances (from Google Maps Distance Matrix API)
- Heuristic: Straight-line distance to goal (Haversine)
"""


class RouteOptimizationProblem:
    """
    The problem of finding an optimal route between two cities in NY State.
    
    A state is represented as a city name (string).
    The goal is to reach the destination city with minimum total distance traveled.
    
    Attributes:
        initial: Starting city name (string)
        goal: Destination city name (string)
        graph: Reference to the CityGraph object (passed in, not global)
    """
    
    def __init__(self, initial, goal, graph):
        """
        Initialize the route optimization problem.
        
        Args:
            initial: Starting city name (e.g., "Buffalo")
            goal: Destination city name (e.g., "New York City")
            graph: Initialized CityGraph object
        
        Raises:
            ValueError: If cities not found in graph
        """
        self.initial = initial
        self.goal = goal
        self.graph = graph
        
        if self.graph is None:
            raise ValueError("CityGraph not initialized. Initialize with city_graph = initialize_city_graph()")
        
        # Validate cities exist
        valid_cities = self.graph.get_all_cities()
        if initial not in valid_cities:
            raise ValueError(f"Initial city '{initial}' not found in graph")
        if goal not in valid_cities:
            raise ValueError(f"Goal city '{goal}' not found in graph")
    
    def actions(self, state):
        """
        Return the actions (possible next cities) from the given state.
        
        An action is moving to a neighboring city.
        
        Args:
            state: Current city name (string)
        
        Returns:
            List of neighboring city names (strings)
        """
        neighbors = self.graph.get_neighbors(state)
        return list(neighbors.keys())
    
    def result(self, state, action):
        """
        Return the state resulting from executing the given action in state.
        
        The action is a neighboring city, so we simply return that city.
        
        Args:
            state: Current city name (string)
            action: Next city to move to (string) - must be a neighbor
        
        Returns:
            The next city name (string)
        """
        # In this problem, the action IS the next state (the city to move to)
        return action
    
    def goal_test(self, state):
        """
        Check if the given state is the goal state.
        
        Args:
            state: City name to test (string)
        
        Returns:
            True if state is the goal city, False otherwise
        """
        return state == self.goal
    
    def path_cost(self, cost_so_far, current_city, action, next_city):
        """
        Calculate the cost of moving from current_city to next_city.
        
        The cost is the driving distance between the two cities (from Google Maps).
        
        Args:
            cost_so_far: Cumulative cost to reach current_city (float)
            current_city: Current city name (string)
            action: Next city name (string)
            next_city: The city we're moving to (string) - same as action
        
        Returns:
            Updated cumulative cost (float)
        """
        distance = self.graph.get_distance(current_city, next_city)
        if distance is None:
            return float('inf')  # Not a valid path
        return cost_so_far + distance
    
    def h(self, node):
        """
        Heuristic function for A* and Greedy search.
        
        Returns the straight-line distance (Haversine) from the node's state
        to the goal. This is an admissible heuristic because straight-line
        distance is always <= actual driving distance.
        
        Args:
            node: A Node object containing a state (city name)
        
        Returns:
            Estimated distance to goal in miles (float)
        """
        # node.state is the current city
        return self.graph.haversine_distance(node.state, self.goal)
    def h_euclidean(self, node):
        """Euclidean distance heuristic"""
        return self.graph.euclidean_distance(node.state, self.goal)
    
    def h_manhattan(self, node):
        """Manhattan distance heuristic"""
        return self.graph.manhattan_distance(node.state, self.goal)
    
    def h_min_graph(self, node):
        """Minimum graph distance heuristic"""
        return self.graph.min_graph_distance(node.state, self.goal)
    
    def h_weighted(self, node):
        """Weighted combination heuristic"""
        return self.graph.weighted_heuristic(node.state, self.goal)
    
    def __repr__(self):
        """String representation for debugging."""
        return f"RouteOptimization({self.initial} -> {self.goal})"