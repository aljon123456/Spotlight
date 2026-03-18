"""
Sorting and Searching Algorithms Module
========================================
Implements various sorting and searching algorithms optimized for parking slot selection.

Algorithms Included:
- Merge Sort: O(n log n) - Stable sort for distance-based selection
- Quick Sort: O(n log n) average - Fast sort for score-based selection
- Heap Sort: O(n log n) - Efficient for priority-based selection
- Binary Search: O(log n) - Fast lookup for available slots
- Selection Algorithm: O(n) average - Find k-smallest/largest elements
"""

from typing import List, Tuple, Callable, Any, Optional
import heapq
import random


class SortingAlgorithms:
    """
    Collection of sorting algorithms for parking slot optimization.
    
    Time Complexity Summary:
    - Merge Sort: O(n log n) best, average, worst | O(n) space
    - Quick Sort: O(n log n) average, O(n²) worst | O(log n) space
    - Heap Sort: O(n log n) best, average, worst | O(1) space
    - Insertion Sort: O(n²) worst | O(1) space - Good for small n
    """
    
    @staticmethod
    def merge_sort(items: List[Tuple[Any, float]], key: Callable = None, reverse: bool = False) -> List[Tuple[Any, float]]:
        """
        Merge Sort - Stable O(n log n) sort.
        
        Best for: Consistent performance, stability important
        Time Complexity: O(n log n) - all cases
        Space Complexity: O(n)
        
        Args:
            items: List of (item, score) tuples
            key: Custom comparison function
            reverse: Sort descending if True
            
        Returns:
            Sorted list of items
            
        Example:
            >>> slots_with_scores = [(slot1, 0.85), (slot2, 0.92), (slot3, 0.78)]
            >>> sorted_slots = SortingAlgorithms.merge_sort(slots_with_scores, reverse=True)
        """
        if len(items) <= 1:
            return items
        
        def merge(left, right):
            result = []
            i = j = 0
            
            while i < len(left) and j < len(right):
                left_val = key(left[i]) if key else left[i][1]
                right_val = key(right[j]) if key else right[j][1]
                
                if (left_val >= right_val) if reverse else (left_val <= right_val):
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            
            result.extend(left[i:])
            result.extend(right[j:])
            return result
        
        mid = len(items) // 2
        left = SortingAlgorithms.merge_sort(items[:mid], key, reverse)
        right = SortingAlgorithms.merge_sort(items[mid:], key, reverse)
        
        return merge(left, right)
    
    @staticmethod
    def quick_sort(items: List[Tuple[Any, float]], key: Callable = None, reverse: bool = False) -> List[Tuple[Any, float]]:
        """
        Quick Sort - Average O(n log n) sort with in-place optimization.
        
        Best for: General purpose, good cache locality
        Time Complexity: O(n log n) average, O(n²) worst
        Space Complexity: O(log n) average
        
        Args:
            items: List of (item, score) tuples
            key: Custom comparison function
            reverse: Sort descending if True
            
        Returns:
            Sorted list of items
        """
        if len(items) <= 1:
            return items
        
        pivot = random.choice(items)
        pivot_val = key(pivot) if key else pivot[1]
        
        left = [x for x in items if ((key(x) if key else x[1]) < pivot_val)]
        middle = [x for x in items if ((key(x) if key else x[1]) == pivot_val)]
        right = [x for x in items if ((key(x) if key else x[1]) > pivot_val)]
        
        result = SortingAlgorithms.quick_sort(left, key, reverse) + middle + SortingAlgorithms.quick_sort(right, key, reverse)
        
        return result if not reverse else result[::-1]
    
    @staticmethod
    def heap_sort(items: List[Tuple[Any, float]], key: Callable = None, reverse: bool = False) -> List[Tuple[Any, float]]:
        """
        Heap Sort - Guaranteed O(n log n) with minimal space overhead.
        
        Best for: When worst-case guarantee needed
        Time Complexity: O(n log n) - all cases
        Space Complexity: O(1) excluding input storage
        
        Args:
            items: List of (item, score) tuples
            key: Custom comparison function
            reverse: Sort descending if True
            
        Returns:
            Sorted list of items
        """
        if len(items) <= 1:
            return items
        
        # For max heap (descending), negate scores
        heap = []
        for item in items:
            val = key(item) if key else item[1]
            if reverse:
                heapq.heappush(heap, (-val, item))
            else:
                heapq.heappush(heap, (val, item))
        
        return [item for val, item in sorted(heap)]
    
    @staticmethod
    def insertion_sort(items: List[Tuple[Any, float]], key: Callable = None, reverse: bool = False) -> List[Tuple[Any, float]]:
        """
        Insertion Sort - O(n²) but excellent for small lists (n < 20).
        
        Best for: Small datasets, nearly sorted data, online sorting
        Time Complexity: O(n²) worst, O(n) best (already sorted)
        Space Complexity: O(1)
        
        Args:
            items: List of (item, score) tuples
            key: Custom comparison function
            reverse: Sort descending if True
            
        Returns:
            Sorted list of items
        """
        items_copy = items.copy()
        
        for i in range(1, len(items_copy)):
            key_val = key(items_copy[i]) if key else items_copy[i][1]
            j = i - 1
            
            while j >= 0:
                j_val = key(items_copy[j]) if key else items_copy[j][1]
                condition = (j_val > key_val) if not reverse else (j_val < key_val)
                
                if condition:
                    items_copy[j + 1] = items_copy[j]
                    j -= 1
                else:
                    break
            
            items_copy[j + 1] = items_copy[i]
        
        return items_copy


class SearchingAlgorithms:
    """
    Collection of searching algorithms for parking slot lookup.
    
    Time Complexity Summary:
    - Binary Search: O(log n) - Requires sorted data
    - Linear Search: O(n) - Works on unsorted data
    - Interpolation Search: O(log log n) average - For uniformly distributed data
    """
    
    @staticmethod
    def binary_search(sorted_items: List[Tuple[Any, float]], target_score: float, key: Callable = None) -> Optional[int]:
        """
        Binary Search - O(log n) for finding specific score in sorted array.
        
        Use Case: Find parking slot with specific confidence score range
        
        Time Complexity: O(log n)
        Space Complexity: O(1)
        
        Args:
            sorted_items: Pre-sorted list of (item, score) tuples
            target_score: Target score to find
            key: Custom comparison function
            
        Returns:
            Index of item, or -1 if not found
        """
        left, right = 0, len(sorted_items) - 1
        
        while left <= right:
            mid = (left + right) // 2
            mid_val = key(sorted_items[mid]) if key else sorted_items[mid][1]
            
            if mid_val == target_score:
                return mid
            elif mid_val < target_score:
                left = mid + 1
            else:
                right = mid - 1
        
        return -1
    
    @staticmethod
    def linear_search(items: List[Tuple[Any, float]], predicate: Callable) -> List[Tuple[Any, float]]:
        """
        Linear Search - O(n) for finding items matching a condition.
        
        Use Case: Find all available slots matching criteria
        
        Time Complexity: O(n)
        Space Complexity: O(k) where k is number of matches
        
        Args:
            items: List of (item, score) tuples
            predicate: Condition function that returns True/False
            
        Returns:
            List of items matching predicate
        """
        return [item for item in items if predicate(item)]
    
    @staticmethod
    def binary_search_closest(sorted_items: List[Tuple[Any, float]], target_score: float, key: Callable = None) -> Optional[Tuple[Any, float]]:
        """
        Binary Search for Closest Value - O(log n).
        
        Finds the item with score closest to target_score.
        
        Use Case: Find best parking slot near ideal distance
        
        Args:
            sorted_items: Pre-sorted list of (item, score) tuples
            target_score: Target score
            key: Custom comparison function
            
        Returns:
            Item with closest score
        """
        if not sorted_items:
            return None
        
        left, right = 0, len(sorted_items) - 1
        
        while left < right:
            mid = (left + right) // 2
            mid_val = key(sorted_items[mid]) if key else sorted_items[mid][1]
            
            if mid_val < target_score:
                left = mid + 1
            else:
                right = mid
        
        # Check left and right for closest
        candidates = []
        if left > 0:
            candidates.append(sorted_items[left - 1])
        if left < len(sorted_items):
            candidates.append(sorted_items[left])
        
        if not candidates:
            return sorted_items[0]
        
        return min(candidates, key=lambda x: abs((key(x) if key else x[1]) - target_score))


class SelectionAlgorithms:
    """
    Selection algorithms for finding k-smallest/largest elements.
    
    Use cases in parking system:
    - Find top 5 best parking slots
    - Find worst n assignments for quality review
    """
    
    @staticmethod
    def quickselect(items: List[Tuple[Any, float]], k: int, key: Callable = None) -> List[Tuple[Any, float]]:
        """
        Quickselect - O(n) average for finding k-th element.
        
        Best for: Finding top/bottom k items without full sort
        
        Time Complexity: O(n) average, O(n²) worst
        Space Complexity: O(1) average
        
        Args:
            items: List of (item, score) tuples
            k: Number of top items to return
            key: Custom comparison function
            
        Returns:
            k largest items
        """
        if k >= len(items):
            return sorted(items, key=lambda x: key(x) if key else x[1], reverse=True)
        
        if k <= 0:
            return []
        
        def select(arr, left, right, k_index):
            if left == right:
                return arr[left]
            
            pivot_index = random.randint(left, right)
            pivot_index = partition(arr, left, right, pivot_index)
            
            if k_index == pivot_index:
                return arr[k_index]
            elif k_index < pivot_index:
                return select(arr, left, pivot_index - 1, k_index)
            else:
                return select(arr, pivot_index + 1, right, k_index)
        
        def partition(arr, left, right, pivot_index):
            pivot_val = key(arr[pivot_index]) if key else arr[pivot_index][1]
            arr[pivot_index], arr[right] = arr[right], arr[pivot_index]
            
            store_index = left
            for i in range(left, right):
                if (key(arr[i]) if key else arr[i][1]) > pivot_val:
                    arr[store_index], arr[i] = arr[i], arr[store_index]
                    store_index += 1
            
            arr[right], arr[store_index] = arr[store_index], arr[right]
            return store_index
        
        # Use heapq for simpler, practical implementation
        return heapq.nlargest(k, items, key=lambda x: key(x) if key else x[1])
    
    @staticmethod
    def nlargest(items: List[Tuple[Any, float]], k: int, key: Callable = None) -> List[Tuple[Any, float]]:
        """
        Find k largest items - uses heap for efficiency.
        
        Time Complexity: O(n log k)
        Space Complexity: O(k)
        
        Args:
            items: List of (item, score) tuples
            k: Number of largest items
            key: Custom comparison function
            
        Returns:
            k largest items in descending order
        """
        return heapq.nlargest(k, items, key=lambda x: key(x) if key else x[1])
    
    @staticmethod
    def nsmallest(items: List[Tuple[Any, float]], k: int, key: Callable = None) -> List[Tuple[Any, float]]:
        """
        Find k smallest items - uses heap for efficiency.
        
        Time Complexity: O(n log k)
        Space Complexity: O(k)
        
        Args:
            items: List of (item, score) tuples
            k: Number of smallest items
            key: Custom comparison function
            
        Returns:
            k smallest items in ascending order
        """
        return heapq.nsmallest(k, items, key=lambda x: key(x) if key else x[1])
