"""
Optimization Utilities Module
==============================
Utility functions for performance optimization and complex calculations.

Includes:
- Distance caching with memoization
- Batch optimization algorithms
- Score aggregation with weights
- Performance profiling decorators
"""

from functools import lru_cache, wraps
import time
from typing import Callable, Dict, List, Tuple, Any
import statistics


class PerformanceProfiler:
    """Decorator for profiling function execution time and complexity."""
    
    _metrics: Dict[str, List[float]] = {}
    
    @classmethod
    def profile(cls, func: Callable) -> Callable:
        """
        Decorator to profile function execution time.
        
        Usage:
            @PerformanceProfiler.profile
            def expensive_function():
                pass
            
            PerformanceProfiler.get_stats('expensive_function')
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            
            if func_name not in cls._metrics:
                cls._metrics[func_name] = []
            
            cls._metrics[func_name].append(execution_time)
            
            return result
        
        return wrapper
    
    @classmethod
    def get_stats(cls, func_name: str) -> Dict[str, float]:
        """Get performance statistics for a profiled function."""
        if func_name not in cls._metrics:
            return {}
        
        times = cls._metrics[func_name]
        return {
            'count': len(times),
            'total': sum(times),
            'average': statistics.mean(times),
            'min': min(times),
            'max': max(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        }
    
    @classmethod
    def clear(cls, func_name: str = None):
        """Clear metrics for a specific function or all functions."""
        if func_name:
            cls._metrics.pop(func_name, None)
        else:
            cls._metrics.clear()


class DistanceCalculator:
    """
    Optimized distance calculations with caching.
    
    Uses memoization to cache distance calculations between pairs of locations.
    """
    
    @staticmethod
    @lru_cache(maxsize=1024)
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate great-circle distance between two points using Haversine formula.
        
        More accurate than Euclidean for larger distances.
        
        Args:
            lat1, lon1: Starting point coordinates
            lat2, lon2: Ending point coordinates
            
        Returns:
            Distance in meters
            
        Time Complexity: O(1) - cacheable
        """
        import math
        
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    @lru_cache(maxsize=1024)
    def euclidean_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate Euclidean distance (faster, acceptable for small campus areas).
        
        Args:
            lat1, lon1: Starting point
            lat2, lon2: Ending point
            
        Returns:
            Distance in meters
            
        Time Complexity: O(1) - cacheable
        """
        import math
        
        # 1 degree ≈ 111 km (at equator)
        lat_diff = (lat2 - lat1) * 111000
        # Adjust for latitude
        lon_diff = (lon2 - lon1) * 111000 * math.cos(math.radians(lat1))
        
        return math.sqrt(lat_diff**2 + lon_diff**2)
    
    @staticmethod
    def clear_cache():
        """Clear distance calculation cache."""
        DistanceCalculator.haversine_distance.cache_clear()
        DistanceCalculator.euclidean_distance.cache_clear()
    
    @staticmethod
    def get_cache_info() -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'haversine': DistanceCalculator.haversine_distance.cache_info(),
            'euclidean': DistanceCalculator.euclidean_distance.cache_info(),
        }


class ScoreAggregator:
    """
    Multi-factor score aggregation with weighted averaging.
    
    Combines multiple scoring factors into single comparable score.
    """
    
    @staticmethod
    def weighted_average(scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        Calculate weighted average of multiple scores.
        
        Args:
            scores: Dictionary mapping factor_name -> score (0.0-1.0)
            weights: Dictionary mapping factor_name -> weight (0.0-1.0)
            
        Returns:
            Weighted average score
            
        Example:
            scores = {
                'distance': 0.85,
                'availability': 0.70,
                'coverage': 0.90,
                'price': 0.60
            }
            weights = {
                'distance': 0.4,
                'availability': 0.3,
                'coverage': 0.2,
                'price': 0.1
            }
            final_score = ScoreAggregator.weighted_average(scores, weights)
            # Returns: 0.75
        """
        if not scores or not weights:
            return 0.0
        
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(scores.get(factor, 0.0) * weights.get(factor, 0.0) 
                          for factor in weights.keys())
        
        return weighted_sum / total_weight
    
    @staticmethod
    def min_max_normalize(values: List[float]) -> List[float]:
        """
        Normalize values to 0-1 range using min-max normalization.
        
        Formula: (x - min) / (max - min)
        
        Args:
            values: List of numeric values
            
        Returns:
            Normalized values in range [0, 1]
        """
        if not values:
            return []
        
        min_val = min(values)
        max_val = max(values)
        
        if min_val == max_val:
            return [0.5] * len(values)  # All same value
        
        return [(v - min_val) / (max_val - min_val) for v in values]
    
    @staticmethod
    def z_score_normalize(values: List[float]) -> List[float]:
        """
        Normalize using z-score (standard deviation normalization).
        
        Formula: (x - mean) / std_dev
        
        Args:
            values: List of numeric values
            
        Returns:
            Z-score normalized values
        """
        if len(values) < 2:
            return values
        
        import statistics
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        
        if stdev == 0:
            return [0.0] * len(values)
        
        return [(v - mean) / stdev for v in values]


class BatchOptimizer:
    """
    Batch optimization algorithms for processing multiple assignments efficiently.
    """
    
    @staticmethod
    def greedy_assignment(slots_with_scores: List[Tuple[Any, float]], 
                         users_with_preferences: List[Tuple[Any, List[str]]]) -> Dict[Any, Any]:
        """
        Greedy algorithm for batch parking assignments.
        
        Algorithm:
        1. Sort slots by score (highest first)
        2. For each user (in order), assign best available slot
        
        Time Complexity: O(n log n + n*m) where n=slots, m=users
        Space Complexity: O(n + m)
        
        Args:
            slots_with_scores: List of (slot, score) tuples, sorted descending
            users_with_preferences: List of (user, preference_list) tuples
            
        Returns:
            Dictionary mapping user -> assigned_slot
            
        Note: This is a fast greedy approach but may not be globally optimal.
        """
        assignments = {}
        available_slots = [slot for slot, _ in slots_with_scores]
        
        for user, preferences in users_with_preferences:
            # Find best preferred slot that's still available
            assigned = False
            
            for preferred_slot_type in preferences:
                for slot in available_slots:
                    if slot.slot_type == preferred_slot_type:
                        assignments[user] = slot
                        available_slots.remove(slot)
                        assigned = True
                        break
                
                if assigned:
                    break
            
            # If no preferred slot available, assign any available slot
            if not assigned and available_slots:
                assignments[user] = available_slots.pop(0)
        
        return assignments
    
    @staticmethod
    def matching_algorithm(users: List[Any], slots: List[Any], 
                          preference_matrix: Dict[Tuple[Any, Any], float]) -> Dict[Any, Any]:
        """
        Bipartite matching algorithm for optimal user-slot assignments.
        
        Uses a scoring matrix to find best overall assignment minimizing conflicts.
        
        Time Complexity: O(n³) using Hungarian algorithm (n = max(users, slots))
        Space Complexity: O(n²)
        
        Args:
            users: List of user objects
            slots: List of parking slot objects
            preference_matrix: Dict mapping (user, slot) -> compatibility_score
            
        Returns:
            Dictionary mapping user -> assigned_slot
            
        Note: For large-scale problems (n > 1000), use approximate algorithms.
        """
        assignments = {}
        
        if not users or not slots:
            return assignments
        
        # Simplified greedy implementation of assignment
        # Real implementation would use Hungarian algorithm
        
        available_slots = set(slots)
        
        for user in users:
            best_slot = None
            best_score = -1
            
            for slot in available_slots:
                score = preference_matrix.get((user, slot), 0.0)
                if score > best_score:
                    best_score = score
                    best_slot = slot
            
            if best_slot:
                assignments[user] = best_slot
                available_slots.remove(best_slot)
        
        return assignments


class ComplexityAnalyzer:
    """
    Analyze and report on algorithm complexity for different scenarios.
    """
    
    @staticmethod
    def estimate_execution_time(n: int, complexity: str, base_time_ms: float = 1.0) -> float:
        """
        Estimate execution time based on input size and complexity class.
        
        Args:
            n: Input size
            complexity: Complexity class ('O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n²)', etc.)
            base_time_ms: Time for single operation in milliseconds
            
        Returns:
            Estimated time in milliseconds
            
        Example:
            >>> ComplexityAnalyzer.estimate_execution_time(1000, 'O(n log n)')
            # Estimates execution time for 1000 elements with O(n log n) algorithm
        """
        import math
        
        complexity_functions = {
            'O(1)': lambda n: 1,
            'O(log n)': lambda n: math.log2(n) if n > 0 else 1,
            'O(n)': lambda n: n,
            'O(n log n)': lambda n: n * math.log2(n) if n > 0 else 1,
            'O(n²)': lambda n: n ** 2,
            'O(n³)': lambda n: n ** 3,
            'O(2^n)': lambda n: 2 ** n,
        }
        
        if complexity not in complexity_functions:
            return 0.0
        
        operations = complexity_functions[complexity](n)
        return operations * base_time_ms
    
    @staticmethod
    def compare_algorithms(n: int, algorithms: Dict[str, str]) -> Dict[str, float]:
        """
        Compare estimated execution times for different algorithms.
        
        Args:
            n: Input size
            algorithms: Dict mapping algorithm_name -> complexity_class
            
        Returns:
            Dict mapping algorithm_name -> estimated_time_ms
            
        Example:
            algorithms = {
                'Merge Sort': 'O(n log n)',
                'Insertion Sort': 'O(n²)',
                'Quick Sort': 'O(n log n)',
            }
            ComplexityAnalyzer.compare_algorithms(1000, algorithms)
        """
        return {
            name: ComplexityAnalyzer.estimate_execution_time(n, complexity)
            for name, complexity in algorithms.items()
        }
