"""
Graph algorithms for pathfinding and distance optimization.
Implements: Dijkstra, A*, Floyd-Warshall, and BFS for optimal route finding.
"""
from typing import Dict, List, Tuple, Optional
from ..models import Building, ParkingLot
import math
from dataclasses import dataclass


@dataclass
class Coordinate:
    """Simple coordinate representation."""
    x: float
    y: float
    
    def distance_to(self, other: 'Coordinate') -> float:
        """Calculate Euclidean distance to another coordinate."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class GraphEngine:
    """Graph-based algorithms for optimal parking location selection."""
    
    @staticmethod
    def dijkstra(graph: Dict[str, Dict[str, float]], start: str, end: str) -> Tuple[float, List[str]]:
        """
        Dijkstra's Algorithm - O((V + E) log V) with min-heap.
        Finds shortest path between two nodes.
        """
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        previous = {node: None for node in graph}
        unvisited = set(graph.keys())
        
        while unvisited:
            # Find unvisited node with minimum distance
            current = min(unvisited, key=lambda x: distances[x])
            
            if distances[current] == float('inf'):
                break
            
            if current == end:
                # Reconstruct path
                path = []
                node = end
                while node is not None:
                    path.append(node)
                    node = previous[node]
                return distances[end], path[::-1]
            
            for neighbor, weight in graph.get(current, {}).items():
                if neighbor in unvisited:
                    new_dist = distances[current] + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        previous[neighbor] = current
            
            unvisited.remove(current)
        
        return distances[end], []
    
    @staticmethod
    def a_star(graph: Dict[str, Dict[str, float]], start: str, end: str, heuristic: Dict[str, float]) -> Tuple[float, List[str]]:
        """
        A* Algorithm - O((V + E) log V) with good heuristics.
        More efficient than Dijkstra when good heuristic available.
        """
        open_set = {start}
        came_from = {}
        g_score = {node: float('inf') for node in graph}
        g_score[start] = 0
        f_score = {node: float('inf') for node in graph}
        f_score[start] = heuristic.get(start, 0)
        
        while open_set:
            current = min(open_set, key=lambda x: f_score[x])
            
            if current == end:
                path = [end]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return g_score[end], path[::-1]
            
            open_set.remove(current)
            
            for neighbor, weight in graph.get(current, {}).items():
                tentative_g = g_score[current] + weight
                
                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = g_score[neighbor] + heuristic.get(neighbor, 0)
                    open_set.add(neighbor)
        
        return float('inf'), []
    
    @staticmethod
    def floyd_warshall(graph: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """
        Floyd-Warshall Algorithm - O(V³) but all-pairs shortest paths.
        Pre-compute for multiple queries. Use when many distance queries needed.
        """
        nodes = list(graph.keys())
        dist = {}
        
        for i in nodes:
            dist[i] = {}
            for j in nodes:
                if i == j:
                    dist[i][j] = 0
                elif j in graph.get(i, {}):
                    dist[i][j] = graph[i][j]
                else:
                    dist[i][j] = float('inf')
        
        for k in nodes:
            for i in nodes:
                for j in nodes:
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        
        return dist
    
    @staticmethod
    def bfs_shortest_path(graph: Dict[str, List[str]], start: str, end: str) -> List[str]:
        """
        BFS (Breadth-First Search) - O(V + E) complexity.
        Optimal for unweighted graphs. Finds minimum hop path.
        """
        from collections import deque
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            node, path = queue.popleft()
            
            if node == end:
                return path
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    @staticmethod
    def nearest_neighbor_tsp(parking_lots: List[Tuple[str, float, float]], start_idx: int = 0) -> Tuple[float, List[int]]:
        """
        Nearest Neighbor TSP - O(n²) heuristic for Traveling Salesman Problem.
        Good for finding efficient parking lot sequence for assignments.
        """
        n = len(parking_lots)
        unvisited = set(range(n))
        current = start_idx
        path = [current]
        unvisited.remove(current)
        total_distance = 0
        
        while unvisited:
            nearest = min(unvisited, 
                         key=lambda x: math.sqrt(
                             (parking_lots[current][1] - parking_lots[x][1]) ** 2 +
                             (parking_lots[current][2] - parking_lots[x][2]) ** 2
                         ))
            
            distance = math.sqrt(
                (parking_lots[current][1] - parking_lots[nearest][1]) ** 2 +
                (parking_lots[current][2] - parking_lots[nearest][2]) ** 2
            )
            
            total_distance += distance
            path.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return total_distance, path
    
    @staticmethod
    def build_location_graph(buildings: List[Building], parking_lots: List[ParkingLot]) -> Dict[str, Dict[str, float]]:
        """
        Build a graph of locations with distances.
        Used for Dijkstra and A* pathfinding.
        """
        graph = {}
        locations = []
        
        # Add buildings
        for building in buildings:
            locations.append(('building', building.id, building.code, 0, 0))  # Placeholder coords
        
        # Add parking lots
        for lot in parking_lots:
            locations.append(('lot', lot.id, lot.name, 0, 0))
        
        # Create edges with distances
        for i, loc1 in enumerate(locations):
            graph[f"{loc1[0]}_{loc1[1]}"] = {}
            for j, loc2 in enumerate(locations):
                if i != j:
                    # Simplified distance calculation
                    distance = abs(i - j)  # Replace with actual coordinates
                    graph[f"{loc1[0]}_{loc1[1]}"][f"{loc2[0]}_{loc2[1]}"] = distance
        
        return graph
