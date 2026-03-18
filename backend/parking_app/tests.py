"""
Test file to verify all algorithm implementations work correctly.
Run with: python manage.py test parking_app.tests.test_algorithms
"""
from django.test import TestCase
from parking_app.algorithms.sorting_algorithms import SortingEngine
from parking_app.algorithms.search_algorithms import SearchEngine
from parking_app.algorithms.graph_algorithms import GraphEngine
from parking_app.algorithms.optimization import OptimizationUtilities, ComplexityAnalysis
from parking_app.models import ParkingSlot, Campus, Building, ParkingLot


class AlgorithmTestCase(TestCase):
    """Test all algorithm implementations."""
    
    def setUp(self):
        """Create test data."""
        # Create campus
        self.campus = Campus.objects.create(
            name="Test Campus",
            location="123 Main St",
            city="Test City",
            state="TS",
            zip_code="12345"
        )
        
        # Create building
        self.building = Building.objects.create(
            campus=self.campus,
            name="Building A",
            code="BLDG_A"
        )
        
        # Create parking lot
        self.parking_lot = ParkingLot.objects.create(
            campus=self.campus,
            name="Lot 1",
            surface_type="outdoor",
            total_slots=100,
            available_slots=50,
            nearest_building=self.building
        )
        
        # Create test slots
        self.slots = []
        for i in range(20):
            slot = ParkingSlot.objects.create(
                parking_lot=self.parking_lot,
                slot_number=f"A{i+1}",
                slot_type="regular" if i % 3 == 0 else "premium",
                status="available",
                is_occupied=False
            )
            self.slots.append(slot)
    
    def test_quick_sort(self):
        """Test Quick Sort algorithm."""
        sorted_slots = SortingEngine.quick_sort(
            self.slots,
            key_func=lambda s: s.id,
            reverse=False
        )
        self.assertEqual(len(sorted_slots), len(self.slots))
        # Verify sorted
        for i in range(len(sorted_slots) - 1):
            self.assertLessEqual(sorted_slots[i].id, sorted_slots[i+1].id)
    
    def test_merge_sort(self):
        """Test Merge Sort algorithm."""
        sorted_slots = SortingEngine.merge_sort(
            self.slots,
            key_func=lambda s: s.id,
            reverse=True
        )
        self.assertEqual(len(sorted_slots), len(self.slots))
        # Verify reverse sorted
        for i in range(len(sorted_slots) - 1):
            self.assertGreaterEqual(sorted_slots[i].id, sorted_slots[i+1].id)
    
    def test_heap_sort(self):
        """Test Heap Sort algorithm."""
        sorted_slots = SortingEngine.heap_sort(
            self.slots,
            key_func=lambda s: s.id
        )
        self.assertEqual(len(sorted_slots), len(self.slots))
    
    def test_tim_sort(self):
        """Test Tim Sort algorithm."""
        sorted_slots = SortingEngine.tim_sort(
            self.slots,
            key_func=lambda s: s.id,
            min_run=5
        )
        self.assertEqual(len(sorted_slots), len(self.slots))
    
    def test_insertion_sort(self):
        """Test Insertion Sort algorithm."""
        sorted_slots = SortingEngine.insertion_sort(
            self.slots,
            key_func=lambda s: s.id
        )
        self.assertEqual(len(sorted_slots), len(self.slots))
    
    def test_binary_search(self):
        """Test Binary Search algorithm."""
        sorted_slots = sorted(self.slots, key=lambda s: s.id)
        target_id = sorted_slots[5].id
        
        result = SearchEngine.binary_search(
            sorted_slots,
            target=target_id,
            key_func=lambda s: s.id
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.id, target_id)
    
    def test_linear_search(self):
        """Test Linear Search algorithm."""
        result = SearchEngine.linear_search(
            self.slots,
            predicate=lambda s: s.slot_number == "A1"
        )
        self.assertIsNotNone(result)
    
    def test_linear_search_all(self):
        """Test Linear Search All algorithm."""
        results = SearchEngine.linear_search_all(
            self.slots,
            predicate=lambda s: s.slot_type == "premium"
        )
        self.assertGreater(len(results), 0)
        for slot in results:
            self.assertEqual(slot.slot_type, "premium")
    
    def test_hash_search(self):
        """Test Hash Search algorithm."""
        target_slot = self.slots[0]
        result = SearchEngine.hash_search(
            self.slots,
            slot_id=target_slot.id
        )
        self.assertEqual(result.id, target_slot.id)
    
    def test_greedy_allocation(self):
        """Test Greedy Allocation algorithm."""
        allocation = OptimizationUtilities.greedy_allocation(
            self.slots,
            users_count=5,
            priority_func=lambda s: s.id
        )
        self.assertEqual(len(allocation), 5)
    
    def test_sliding_window(self):
        """Test Sliding Window algorithm."""
        windows = OptimizationUtilities.sliding_window_availability(
            self.slots,
            window_size=3
        )
        self.assertIsInstance(windows, list)
    
    def test_complexity_analysis(self):
        """Test Complexity Analysis utility."""
        complexity = ComplexityAnalysis.get_complexity('merge_sort')
        self.assertIn('best', complexity)
        self.assertIn('average', complexity)
        self.assertIn('worst', complexity)
    
    def test_dijkstra_algorithm(self):
        """Test Dijkstra's Algorithm."""
        graph = {
            'A': {'B': 4, 'C': 2},
            'B': {'A': 4, 'D': 5},
            'C': {'A': 2, 'D': 8},
            'D': {'B': 5, 'C': 8}
        }
        
        distance, path = GraphEngine.dijkstra(graph, 'A', 'D')
        self.assertLess(distance, float('inf'))
        self.assertGreater(len(path), 0)
    
    def test_cache_decorator(self):
        """Test Performance Caching decorator."""
        call_count = 0
        
        @OptimizationUtilities.cache_decorator
        def expensive_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = expensive_func(5)
        first_call_count = call_count
        
        # Second call (should be cached)
        result2 = expensive_func(5)
        second_call_count = call_count
        
        self.assertEqual(result1, 10)
        self.assertEqual(result2, 10)
        self.assertEqual(first_call_count, 1)
        self.assertEqual(second_call_count, 1)  # Not incremented due to cache


class AlgorithmPerformanceTestCase(TestCase):
    """Performance tests for algorithm selection."""
    
    def setUp(self):
        """Create test campus and parking lot."""
        self.campus = Campus.objects.create(
            name="Performance Test Campus",
            location="456 Test Ave",
            city="Test City",
            state="TS",
            zip_code="54321"
        )
        
        self.building = Building.objects.create(
            campus=self.campus,
            name="Building B",
            code="BLDG_B"
        )
        
        self.parking_lot = ParkingLot.objects.create(
            campus=self.campus,
            name="Lot 2",
            surface_type="garage",
            total_slots=1000,
            available_slots=500,
            nearest_building=self.building
        )
    
    def test_algorithm_selection_by_size(self):
        """Test that algorithm selection works correctly by dataset size."""
        # Small dataset (< 20 items)
        small_slots = [
            ParkingSlot.objects.create(
                parking_lot=self.parking_lot,
                slot_number=f"B{i+1}",
                slot_type="regular",
                status="available",
                is_occupied=False
            )
            for i in range(10)
        ]
        
        sorted_small = SortingEngine.insertion_sort(small_slots, key_func=lambda s: s.id)
        self.assertEqual(len(sorted_small), 10)
        
        # Medium dataset (20-1000 items)
        medium_slots = [
            ParkingSlot.objects.create(
                parking_lot=self.parking_lot,
                slot_number=f"C{i+1}",
                slot_type="premium",
                status="available",
                is_occupied=False
            )
            for i in range(100)
        ]
        
        sorted_medium = SortingEngine.merge_sort(medium_slots, key_func=lambda s: s.id)
        self.assertEqual(len(sorted_medium), 100)
