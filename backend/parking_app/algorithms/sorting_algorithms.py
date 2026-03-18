"""
Sorting algorithms for parking slot optimization.
Implements: Quick Sort, Merge Sort, Heap Sort with O(n log n) complexity.
"""
from typing import List, Tuple, Callable
from ..models import ParkingSlot


class SortingEngine:
    """Implements multiple sorting algorithms for slot optimization."""
    
    @staticmethod
    def quick_sort(slots: List[ParkingSlot], key_func: Callable, reverse: bool = False) -> List[ParkingSlot]:
        """
        Quick Sort Algorithm - O(n log n) average, O(n²) worst case.
        Ideal for large datasets with good cache performance.
        """
        if len(slots) <= 1:
            return slots
        
        pivot = slots[len(slots) // 2]
        pivot_val = key_func(pivot)
        
        left = [s for s in slots if key_func(s) < pivot_val]
        middle = [s for s in slots if key_func(s) == pivot_val]
        right = [s for s in slots if key_func(s) > pivot_val]
        
        if reverse:
            return SortingEngine.quick_sort(right, key_func, reverse) + middle + SortingEngine.quick_sort(left, key_func, reverse)
        return SortingEngine.quick_sort(left, key_func, reverse) + middle + SortingEngine.quick_sort(right, key_func, reverse)
    
    @staticmethod
    def merge_sort(slots: List[ParkingSlot], key_func: Callable, reverse: bool = False) -> List[ParkingSlot]:
        """
        Merge Sort Algorithm - O(n log n) guaranteed.
        Stable sort, better for linked lists and external sorting.
        """
        if len(slots) <= 1:
            return slots
        
        mid = len(slots) // 2
        left = SortingEngine.merge_sort(slots[:mid], key_func, reverse)
        right = SortingEngine.merge_sort(slots[mid:], key_func, reverse)
        
        return SortingEngine._merge(left, right, key_func, reverse)
    
    @staticmethod
    def _merge(left: List[ParkingSlot], right: List[ParkingSlot], key_func: Callable, reverse: bool) -> List[ParkingSlot]:
        """Merge step for merge sort."""
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            left_val = key_func(left[i])
            right_val = key_func(right[j])
            
            if (left_val <= right_val) != reverse:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    @staticmethod
    def heap_sort(slots: List[ParkingSlot], key_func: Callable, reverse: bool = False) -> List[ParkingSlot]:
        """
        Heap Sort Algorithm - O(n log n) guaranteed.
        In-place sorting with good space efficiency.
        """
        heap = slots.copy()
        n = len(heap)
        
        # Build max/min heap
        for i in range(n // 2 - 1, -1, -1):
            SortingEngine._heapify(heap, n, i, key_func, reverse)
        
        # Extract elements from heap
        result = []
        for i in range(n - 1, 0, -1):
            result.append(heap[0])
            heap[0] = heap[i]
            SortingEngine._heapify(heap, i, 0, key_func, reverse)
        result.append(heap[0])
        
        return result if not reverse else result[::-1]
    
    @staticmethod
    def _heapify(heap: List[ParkingSlot], n: int, i: int, key_func: Callable, reverse: bool):
        """Helper function to maintain heap property."""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and (key_func(heap[left]) > key_func(heap[largest])) != reverse:
            largest = left
        
        if right < n and (key_func(heap[right]) > key_func(heap[largest])) != reverse:
            largest = right
        
        if largest != i:
            heap[i], heap[largest] = heap[largest], heap[i]
            SortingEngine._heapify(heap, n, largest, key_func, reverse)
    
    @staticmethod
    def insertion_sort(slots: List[ParkingSlot], key_func: Callable, reverse: bool = False) -> List[ParkingSlot]:
        """
        Insertion Sort - O(n²) but excellent for small lists and nearly sorted data.
        Used for final polishing in hybrid algorithms.
        """
        result = slots.copy()
        
        for i in range(1, len(result)):
            key_val = key_func(result[i])
            j = i - 1
            
            while j >= 0 and ((key_func(result[j]) > key_val) != reverse):
                result[j + 1] = result[j]
                j -= 1
            
            result[j + 1] = result[i]
        
        return result
    
    @staticmethod
    def tim_sort(slots: List[ParkingSlot], key_func: Callable, reverse: bool = False, min_run: int = 32) -> List[ParkingSlot]:
        """
        Tim Sort - Hybrid algorithm combining merge sort and insertion sort.
        O(n log n) with excellent real-world performance.
        Best for practical applications with mixed data patterns.
        """
        n = len(slots)
        
        # Divide into runs and sort with insertion sort
        runs = []
        for i in range(0, n, min_run):
            run = slots[i:min(i + min_run, n)]
            runs.append(SortingEngine.insertion_sort(run, key_func, reverse))
        
        # Merge runs
        while len(runs) > 1:
            merged_runs = []
            for i in range(0, len(runs), 2):
                if i + 1 < len(runs):
                    merged = SortingEngine._merge(runs[i], runs[i + 1], key_func, reverse)
                    merged_runs.append(merged)
                else:
                    merged_runs.append(runs[i])
            runs = merged_runs
        
        return runs[0] if runs else []
