"""
Search algorithms for efficient parking slot lookup.
Implements: Binary Search, Linear Search with interpolation, B-Tree search.
"""
from typing import List, Optional, Callable, Any
from ..models import ParkingSlot


class SearchEngine:
    """Implements efficient search algorithms for slot discovery."""
    
    @staticmethod
    def binary_search(sorted_slots: List[ParkingSlot], target: Any, key_func: Callable) -> Optional[ParkingSlot]:
        """
        Binary Search - O(log n) complexity.
        Requires pre-sorted list. Most efficient for large sorted datasets.
        """
        left, right = 0, len(sorted_slots) - 1
        
        while left <= right:
            mid = (left + right) // 2
            mid_val = key_func(sorted_slots[mid])
            
            if mid_val == target:
                return sorted_slots[mid]
            elif mid_val < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return None
    
    @staticmethod
    def binary_search_range(sorted_slots: List[ParkingSlot], min_val: Any, max_val: Any, key_func: Callable) -> List[ParkingSlot]:
        """
        Binary Search Range - O(log n + k) where k is result size.
        Finds all slots within a value range.
        """
        def find_left(target):
            left, right = 0, len(sorted_slots)
            while left < right:
                mid = (left + right) // 2
                if key_func(sorted_slots[mid]) < target:
                    left = mid + 1
                else:
                    right = mid
            return left
        
        def find_right(target):
            left, right = 0, len(sorted_slots)
            while left < right:
                mid = (left + right) // 2
                if key_func(sorted_slots[mid]) <= target:
                    left = mid + 1
                else:
                    right = mid
            return left
        
        left_idx = find_left(min_val)
        right_idx = find_right(max_val)
        
        return sorted_slots[left_idx:right_idx]
    
    @staticmethod
    def interpolation_search(sorted_slots: List[ParkingSlot], target: float, key_func: Callable) -> Optional[ParkingSlot]:
        """
        Interpolation Search - O(log log n) average for uniformly distributed data.
        Better than binary search for sorted numeric arrays.
        """
        left, right = 0, len(sorted_slots) - 1
        
        while left <= right and left < len(sorted_slots):
            left_val = key_func(sorted_slots[left])
            right_val = key_func(sorted_slots[right])
            
            if left_val == right_val:
                if left_val == target:
                    return sorted_slots[left]
                return None
            
            # Interpolate position
            pos = int(left + (target - left_val) / (right_val - left_val) * (right - left))
            pos = max(left, min(pos, right))
            
            pos_val = key_func(sorted_slots[pos])
            
            if pos_val == target:
                return sorted_slots[pos]
            elif pos_val < target:
                left = pos + 1
            else:
                right = pos - 1
        
        return None
    
    @staticmethod
    def linear_search(slots: List[ParkingSlot], predicate: Callable[[ParkingSlot], bool]) -> Optional[ParkingSlot]:
        """
        Linear Search - O(n) complexity.
        Use for unsorted data or complex predicates.
        """
        for slot in slots:
            if predicate(slot):
                return slot
        return None
    
    @staticmethod
    def linear_search_all(slots: List[ParkingSlot], predicate: Callable[[ParkingSlot], bool]) -> List[ParkingSlot]:
        """
        Linear Search All - O(n) complexity.
        Returns all matching slots.
        """
        return [slot for slot in slots if predicate(slot)]
    
    @staticmethod
    def hash_search(slots: List[ParkingSlot], slot_id: int) -> Optional[ParkingSlot]:
        """
        Hash Search - O(1) average case.
        Best for direct ID lookups using dictionary/hash table.
        """
        slot_map = {slot.id: slot for slot in slots}
        return slot_map.get(slot_id)
    
    @staticmethod
    def exponential_search(sorted_slots: List[ParkingSlot], target: Any, key_func: Callable) -> Optional[ParkingSlot]:
        """
        Exponential Search - O(log n) complexity.
        Effective when target is near the beginning of the list.
        """
        if not sorted_slots:
            return None
        
        if key_func(sorted_slots[0]) == target:
            return sorted_slots[0]
        
        i = 1
        while i < len(sorted_slots) and key_func(sorted_slots[i]) < target:
            i *= 2
        
        left = i // 2
        right = min(i, len(sorted_slots) - 1)
        
        while left <= right:
            mid = (left + right) // 2
            mid_val = key_func(sorted_slots[mid])
            
            if mid_val == target:
                return sorted_slots[mid]
            elif mid_val < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return None
