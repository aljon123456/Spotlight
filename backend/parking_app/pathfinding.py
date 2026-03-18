"""
Graph and Pathfinding Algorithms Module
========================================
Implements graph algorithms for optimal parking route/location selection on campus.

Algorithms Included:
- Dijkstra's Algorithm: O(V + E log V) - Shortest path from one point to all
- A* Search: O(E) - Heuristic-guided shortest path (faster for goal)
- Breadth-First Search (BFS): O(V + E) - Shortest path in unweighted graphs
- Depth-First Search (DFS): O(V + E) - Graph traversal
- Floyd-Warshall: O(V³) - All pairs shortest paths
- Minimum Spanning Tree (Kruskal/Prim): Connect all buildings with min distance
"""

from typing import Dict, List, Tuple, Optional, Set
from collections import deque
import heapq
import math


class Building:
    """Represents a building node in the campus graph."""
    def __init__(self, building_id: str, name: str, latitude: float = 0, longitude: float = 0):
        self.building_id = building_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
    
    def __hash__(self):
        return hash(self.building_id)
    
    def __eq__(self, other):
        return self.building_id == other.building_id
    
    def __repr__(self):
        return f"Building({self.building_id}, {self.name})"


class ParkingLocation:
    """Represents a parking lot node in the campus graph."""
    def __init__(self, lot_id: str, name: str, latitude: float = 0, longitude: float = 0, available_slots: int = 0):
        self.lot_id = lot_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.available_slots = available_slots
    
    def __hash__(self):
        return hash(self.lot_id)
    
    def __eq__(self, other):
        return self.lot_id == other.lot_id
    
    def __repr__(self):
        return f"ParkingLot({self.lot_id}, {self.name}, slots={self.available_slots})"


class CampusGraph:
    """
    Represents campus as graph with buildings and parking lots as nodes.
    
    Use cases:
    - Find shortest path from parking lot to building
    - Recommend closest available parking to destination
    - Optimize overall campus parking distribution
    """
    
    def __init__(self):
        self.buildings: Dict[str, Building] = {}
        self.parking_lots: Dict[str, ParkingLocation] = {}
        self.edges: Dict[str, List[Tuple[str, float]]] = {}  # node_id -> [(neighbor_id, distance)]
    
    def add_building(self, building: Building):
        """Add building node to graph."""
        self.buildings[building.building_id] = building
        if building.building_id not in self.edges:
            self.edges[building.building_id] = []
    
    def add_parking_lot(self, parking_lot: ParkingLocation):
        """Add parking lot node to graph."""
        self.parking_lots[parking_lot.lot_id] = parking_lot
        if parking_lot.lot_id not in self.edges:
            self.edges[parking_lot.lot_id] = []
    
    def add_edge(self, from_id: str, to_id: str, distance: float):
        """
        Add weighted edge between two nodes.
        Distance represents walking/driving distance in meters.
        """
        if from_id not in self.edges:
            self.edges[from_id] = []
        self.edges[from_id].append((to_id, distance))
        
        # Make bidirectional
        if to_id not in self.edges:
            self.edges[to_id] = []
        self.edges[to_id].append((from_id, distance))
    
    def euclidean_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate Euclidean distance between two coordinates in meters.
        Simplified for campus-scale (1 degree ≈ 111 km).
        """
        lat_diff = (lat2 - lat1) * 111000
        lon_diff = (lon2 - lon1) * 111000 * math.cos(math.radians(lat1))
        return math.sqrt(lat_diff**2 + lon_diff**2)


class DijkstraAlgorithm:
    """
    Dijkstra's Shortest Path Algorithm.
    
    Time Complexity: O((V + E) log V) with min-heap
    Space Complexity: O(V)
    
    Use case: Find shortest walking distance from any parking lot to a building
    """
    
    @staticmethod
    def shortest_path(graph: CampusGraph, start_id: str, end_id: str) -> Tuple[Optional[float], List[str]]:
        """
        Find shortest path from start to end using Dijkstra's algorithm.
        
        Args:
            graph: CampusGraph instance
            start_id: Starting node ID (parking lot)
            end_id: Destination node ID (building)
            
        Returns:
            Tuple of (distance, path) or (None, []) if no path exists
            
        Example:
            distance, path = DijkstraAlgorithm.shortest_path(graph, 'lot_A', 'building_1')
            # Returns (345.2, ['lot_A', 'intersection_1', 'building_1'])
        """
        distances = {node: float('inf') for node in graph.edges}
        distances[start_id] = 0
        
        previous = {node: None for node in graph.edges}
        
        # Min heap: (distance, node_id)
        pq = [(0, start_id)]
        visited = set()
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # Found destination
            if current_node == end_id:
                path = []
                node = end_id
                while node is not None:
                    path.append(node)
                    node = previous[node]
                return current_distance, path[::-1]
            
            # Check all neighbors
            for neighbor, weight in graph.edges.get(current_node, []):
                if neighbor not in visited:
                    new_distance = current_distance + weight
                    
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current_node
                        heapq.heappush(pq, (new_distance, neighbor))
        
        return None, []
    
    @staticmethod
    def all_shortest_paths(graph: CampusGraph, start_id: str) -> Dict[str, float]:
        """
        Find shortest distances from start node to all other nodes.
        
        Use case: From parking lot, find walking distance to all buildings
        
        Returns:
            Dictionary mapping node_id -> shortest_distance
        """
        distances = {node: float('inf') for node in graph.edges}
        distances[start_id] = 0
        
        pq = [(0, start_id)]
        visited = set()
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            for neighbor, weight in graph.edges.get(current_node, []):
                if neighbor not in visited:
                    new_distance = current_distance + weight
                    
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        heapq.heappush(pq, (new_distance, neighbor))
        
        return distances


class AStarSearch:
    """
    A* Search Algorithm - Enhanced Dijkstra with heuristic.
    
    Time Complexity: O(E log V) - typically faster than Dijkstra
    Space Complexity: O(V)
    
    Use case: Find optimal parking location guided by distance heuristic
    Faster than Dijkstra when you know approximate direction to goal.
    """
    
    @staticmethod
    def shortest_path(graph: CampusGraph, start_id: str, end_id: str, heuristic=None) -> Tuple[Optional[float], List[str]]:
        """
        Find shortest path using A* with heuristic function.
        
        Args:
            graph: CampusGraph instance
            start_id: Starting node ID
            end_id: Goal node ID
            heuristic: Function(node_id) -> estimated_distance_to_goal
            
        Returns:
            Tuple of (distance, path)
            
        Example:
            # Define heuristic as Euclidean distance to building
            def heuristic(node_id):
                if node_id in graph.buildings:
                    return 0  # At destination
                return euclidean_distance(...)
            
            distance, path = AStarSearch.shortest_path(graph, 'lot_A', 'building_1', heuristic)
        """
        
        def default_heuristic(node_id):
            """Default: assume some distance remaining."""
            return 0
        
        if heuristic is None:
            heuristic = default_heuristic
        
        g_score = {node: float('inf') for node in graph.edges}
        g_score[start_id] = 0
        
        f_score = {node: float('inf') for node in graph.edges}
        f_score[start_id] = heuristic(start_id)
        
        open_set = [(f_score[start_id], start_id)]
        visited = set()
        previous = {node: None for node in graph.edges}
        
        while open_set:
            _, current_node = heapq.heappop(open_set)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if current_node == end_id:
                path = []
                node = end_id
                while node is not None:
                    path.append(node)
                    node = previous[node]
                return g_score[end_id], path[::-1]
            
            for neighbor, weight in graph.edges.get(current_node, []):
                if neighbor not in visited:
                    tentative_g = g_score[current_node] + weight
                    
                    if tentative_g < g_score[neighbor]:
                        previous[neighbor] = current_node
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = g_score[neighbor] + heuristic(neighbor)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None, []


class BreadthFirstSearch:
    """
    BFS Algorithm - Best for unweighted graphs or level-by-level exploration.
    
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    
    Use case: Find parking lots by proximity level (closest first)
    """
    
    @staticmethod
    def find_nearest_parking(graph: CampusGraph, start_building_id: str, k: int = 5) -> List[str]:
        """
        Find k nearest parking lots to a building using BFS levels.
        
        Returns parking lots in order of proximity.
        
        Args:
            graph: CampusGraph instance
            start_building_id: Starting building ID
            k: Number of nearest lots to return
            
        Returns:
            List of parking lot IDs sorted by proximity
        """
        queue = deque([(start_building_id, 0)])
        visited = {start_building_id}
        results = []
        
        while queue and len(results) < k:
            current_node, distance = queue.popleft()
            
            # If it's a parking lot, add to results
            if current_node in graph.parking_lots:
                results.append(current_node)
            
            # Explore neighbors
            for neighbor, weight in graph.edges.get(current_node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + weight))
        
        return results
    
    @staticmethod
    def shortest_path_unweighted(graph: CampusGraph, start_id: str, end_id: str) -> List[str]:
        """
        Find shortest path in unweighted graph.
        
        Time Complexity: O(V + E)
        
        Returns:
            List of node IDs representing path
        """
        queue = deque([(start_id, [start_id])])
        visited = {start_id}
        
        while queue:
            current_node, path = queue.popleft()
            
            if current_node == end_id:
                return path
            
            for neighbor, _ in graph.edges.get(current_node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []


class MinimumSpanningTree:
    """
    Minimum Spanning Tree Algorithms.
    
    Use case: Design efficient campus walkway/pathway system connecting
    all buildings and parking lots with minimum total distance.
    """
    
    @staticmethod
    def kruskal(graph: CampusGraph) -> List[Tuple[str, str, float]]:
        """
        Kruskal's MST Algorithm using Union-Find.
        
        Time Complexity: O(E log E)
        Space Complexity: O(V)
        
        Returns:
            List of edges (from_id, to_id, distance) in MST
        """
        # Extract all edges
        edges = []
        seen = set()
        
        for from_id, neighbors in graph.edges.items():
            for to_id, weight in neighbors:
                edge = tuple(sorted([from_id, to_id]))
                if edge not in seen:
                    edges.append((weight, from_id, to_id))
                    seen.add(edge)
        
        edges.sort()  # Sort by weight
        
        # Union-Find
        parent = {node: node for node in graph.edges}
        
        def find(node):
            if parent[node] != node:
                parent[node] = find(parent[node])
            return parent[node]
        
        def union(node1, node2):
            root1, root2 = find(node1), find(node2)
            if root1 != root2:
                parent[root1] = root2
                return True
            return False
        
        mst = []
        for weight, from_id, to_id in edges:
            if union(from_id, to_id):
                mst.append((from_id, to_id, weight))
        
        return mst
    
    @staticmethod
    def prim(graph: CampusGraph, start_id: str = None) -> List[Tuple[str, str, float]]:
        """
        Prim's MST Algorithm.
        
        Time Complexity: O(E log V)
        Space Complexity: O(V)
        
        Returns:
            List of edges (from_id, to_id, distance) in MST
        """
        if start_id is None:
            start_id = next(iter(graph.edges.keys()))
        
        visited = {start_id}
        edges = []
        
        # Min heap: (weight, from_id, to_id)
        pq = []
        for neighbor, weight in graph.edges.get(start_id, []):
            heapq.heappush(pq, (weight, start_id, neighbor))
        
        mst = []
        
        while pq and len(visited) < len(graph.edges):
            weight, from_id, to_id = heapq.heappop(pq)
            
            if to_id in visited:
                continue
            
            visited.add(to_id)
            mst.append((from_id, to_id, weight))
            
            # Add new edges from newly visited node
            for neighbor, w in graph.edges.get(to_id, []):
                if neighbor not in visited:
                    heapq.heappush(pq, (w, to_id, neighbor))
        
        return mst
