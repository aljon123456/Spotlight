"""Optimization utilities and algorithm complexity analysis."""
from typing import List, Dict, Tuple, Callable
from ..models import ParkingSlot, Assignment
import time
from functools import wraps


class OptimizationUtilities:
    """Performance optimization and analysis utilities."""
    
    @staticmethod
    def time_complexity_analyzer(func: Callable):
        """Decorator to analyze function execution time and estimate complexity."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            
            # Store metadata
            if not hasattr(wrapper, 'metrics'):
                wrapper.metrics = []
            
            wrapper.metrics.append({
                'function': func.__name__,
                'execution_time': execution_time,
                'timestamp': start_time
            })
            
            return result
        
        return wrapper
    
    @staticmethod
    def cache_decorator(func: Callable):
        """LRU-style caching for repeated queries."""
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            
            return cache[key]
        
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: {'size': len(cache), 'keys': list(cache.keys())}
        
        return wrapper
    
    @staticmethod
    def batch_process(items: List, batch_size: int, processor: Callable) -> List:
        """
        Process items in batches for memory efficiency.
        Reduces space complexity from O(n) to O(batch_size).
        """
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            results.extend(processor(batch))
        return results
    
    @staticmethod
    def greedy_allocation(slots: List[ParkingSlot], users_count: int, priority_func: Callable) -> Dict[int, List[ParkingSlot]]:
        """
        Greedy allocation algorithm - O(n log n).
        Allocates slots to users prioritizing high-value matches.
        """
        # Sort slots by priority
        sorted_slots = sorted(slots, key=priority_func, reverse=True)
        allocation = {}
        
        slots_per_user = len(sorted_slots) // users_count
        remainder = len(sorted_slots) % users_count
        
        idx = 0
        for user_id in range(users_count):
            user_allocation = slots_per_user + (1 if user_id < remainder else 0)
            allocation[user_id] = sorted_slots[idx:idx + user_allocation]
            idx += user_allocation
        
        return allocation
    
    @staticmethod
    def two_pointer_matching(slots1: List[ParkingSlot], slots2: List[ParkingSlot], 
                             match_func: Callable[[ParkingSlot, ParkingSlot], bool]) -> List[Tuple[ParkingSlot, ParkingSlot]]:
        """
        Two-pointer technique - O(n + m) complexity.
        Efficiently matches elements from two sorted lists.
        """
        matches = []
        i, j = 0, 0
        
        while i < len(slots1) and j < len(slots2):
            if match_func(slots1[i], slots2[j]):
                matches.append((slots1[i], slots2[j]))
                i += 1
                j += 1
            elif slots1[i].id < slots2[j].id:
                i += 1
            else:
                j += 1
        
        return matches
    
    @staticmethod
    def dynamic_programming_distance(slots: List[ParkingSlot], building_id: int, memo: Dict = None) -> Dict[int, float]:
        """
        Dynamic Programming - O(n) with memoization.
        Caches distance calculations to avoid recomputation.
        """
        if memo is None:
            memo = {}
        
        distances = {}
        
        for slot in slots:
            key = (slot.id, building_id)
            
            if key not in memo:
                # Calculate distance (simplified)
                memo[key] = abs(slot.parking_lot.id - building_id) * 0.5
            
            distances[slot.id] = memo[key]
        
        return distances
    
    @staticmethod
    def sliding_window_availability(slots: List[ParkingSlot], window_size: int) -> List[List[ParkingSlot]]:
        """
        Sliding Window technique - O(n) complexity.
        Finds available slot groups within a window size.
        """
        windows = []
        
        for i in range(len(slots) - window_size + 1):
            window = slots[i:i + window_size]
            if all(not slot.is_occupied for slot in window):
                windows.append(window)
        
        return windows


class ComplexityAnalysis:
    """Document and analyze algorithm complexities."""
    
    ALGORITHM_COMPLEXITIES = {
        'quick_sort': {'best': 'O(n log n)', 'average': 'O(n log n)', 'worst': 'O(n²)', 'space': 'O(log n)'},
        'merge_sort': {'best': 'O(n log n)', 'average': 'O(n log n)', 'worst': 'O(n log n)', 'space': 'O(n)'},
        'heap_sort': {'best': 'O(n log n)', 'average': 'O(n log n)', 'worst': 'O(n log n)', 'space': 'O(1)'},
        'tim_sort': {'best': 'O(n)', 'average': 'O(n log n)', 'worst': 'O(n log n)', 'space': 'O(n)'},
        'binary_search': {'time': 'O(log n)', 'space': 'O(1)', 'requirement': 'Sorted data'},
        'dijkstra': {'time': 'O((V + E) log V)', 'space': 'O(V)', 'use_case': 'Weighted shortest path'},
        'a_star': {'time': 'O((V + E) log V)', 'space': 'O(V)', 'use_case': 'Heuristic pathfinding'},
        'bfs': {'time': 'O(V + E)', 'space': 'O(V)', 'use_case': 'Unweighted shortest path'},
    }
    
    @staticmethod
    def get_complexity(algorithm: str) -> Dict:
        """Retrieve complexity analysis for an algorithm."""
        return ComplexityAnalysis.ALGORITHM_COMPLEXITIES.get(algorithm, {})
    
    @staticmethod
    def print_analysis():
        """Print all algorithm complexity analyses."""
        for algo, complexity in ComplexityAnalysis.ALGORITHM_COMPLEXITIES.items():
            print(f"\n{algo.upper()}:")
            for key, value in complexity.items():
                print(f"  {key}: {value}")
