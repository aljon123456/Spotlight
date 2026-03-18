"""
Views for parking app.
API endpoints for campus, buildings, lots, slots, schedules, assignments, and notifications.
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from .models import (
    Campus, Building, ParkingLot, ParkingSlot, Schedule,
    Assignment, Notification, AssignmentHistory
)
from .serializers import (
    CampusSerializer, BuildingSerializer, ParkingLotSerializer, ParkingSlotSerializer,
    ScheduleSerializer, AssignmentSerializer, NotificationSerializer, AssignmentHistorySerializer
)
from .assignment_engine import ParkingAssignmentEngine


class CampusViewSet(viewsets.ModelViewSet):
    """
    Campus viewset for CRUD operations.
    Represents university campuses with buildings and parking lots.
    """
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('name', 'city', 'state')
    search_fields = ('name', 'location', 'city')
    ordering_fields = ('name', 'created_at')


class BuildingViewSet(viewsets.ModelViewSet):
    """
    Building viewset for CRUD operations.
    Represents campus buildings where users need parking for classes/work.
    """
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('campus', 'code')
    search_fields = ('name', 'code', 'description')
    ordering_fields = ('name', 'code', 'created_at')


class ParkingLotViewSet(viewsets.ModelViewSet):
    """
    Parking Lot viewset for CRUD operations.
    Represents parking areas on campus with available slots.
    """
    queryset = ParkingLot.objects.all()
    serializer_class = ParkingLotSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('campus', 'surface_type')
    search_fields = ('name',)
    ordering_fields = ('available_slots', 'name', 'created_at')
    
    @action(detail=False, methods=['GET'])
    def available_lots(self, request):
        """Get parking lots with available slots."""
        lots = ParkingLot.objects.filter(available_slots__gt=0)
        serializer = self.get_serializer(lots, many=True)
        return Response(serializer.data)


class ParkingSlotViewSet(viewsets.ModelViewSet):
    """
    Parking Slot viewset for CRUD operations.
    Individual parking spaces that are assigned to users.
    """
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('parking_lot', 'slot_type', 'status')
    search_fields = ('slot_number',)
    ordering_fields = ('slot_number', 'status', 'created_at')
    
    @action(detail=False, methods=['GET'])
    def available_slots(self, request):
        """Get all available parking slots."""
        slots = ParkingSlot.objects.filter(status='available')
        
        # Filter by type if specified
        slot_type = request.query_params.get('type')
        if slot_type:
            slots = slots.filter(slot_type=slot_type)
        
        serializer = self.get_serializer(slots, many=True)
        return Response(serializer.data)


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    Schedule viewset for managing user schedules.
    Stores class and work schedules for parking assignment.
    """
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('schedule_type', 'building')
    ordering_fields = ('start_time', 'created_at')
    
    def get_queryset(self):
        """Filter schedules by current user and only active schedules if not admin."""
        from django.utils import timezone
        today = timezone.now().date()
        
        queryset = Schedule.objects.all()
        
        # Filter by current user if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Filter to only return active schedules (within date range)
        queryset = queryset.filter(start_date__lte=today, end_date__gte=today)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the user to the current authenticated user."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['GET'])
    def my_schedules(self, request):
        """Get current user's active schedules (only within date range)."""
        from django.utils import timezone
        today = timezone.now().date()
        
        schedules = Schedule.objects.filter(
            user=request.user,
            start_date__lte=today,
            end_date__gte=today
        )
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def expired_schedules(self, request):
        """Get user's past/expired schedules (for history/reference)."""
        from django.utils import timezone
        today = timezone.now().date()
        
        schedules = Schedule.objects.filter(
            user=request.user,
            end_date__lt=today
        ).order_by('-end_date')
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def assign_parking(self, request, pk=None):
        """Assign parking slot based on this schedule."""
        schedule = self.get_object()
        
        if schedule.user != request.user:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        engine = ParkingAssignmentEngine()
        assignment = engine.assign_parking(request.user, schedule)
        
        if not assignment:
            return Response(
                {'error': 'No available parking slots for this schedule.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            AssignmentSerializer(assignment).data,
            status=status.HTTP_201_CREATED
        )


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    Assignment viewset for parking assignments.
    Links users to parking slots with schedule information.
    """
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('status', 'parking_slot')
    ordering_fields = ('start_datetime', 'created_at')
    
    def get_queryset(self):
        """Filter assignments by current user if not admin."""
        if self.request.user.is_staff:
            return Assignment.objects.all()
        return Assignment.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['GET'])
    def current_assignment(self, request):
        """Get user's current active assignment."""
        now = timezone.now()
        assignment = Assignment.objects.filter(
            user=request.user,
            status='active',
            start_datetime__lte=now,
            end_datetime__gte=now
        ).first()
        
        if not assignment:
            return Response(
                {'error': 'No current parking assignment.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(AssignmentSerializer(assignment).data)
    
    @action(detail=True, methods=['POST'])
    def explain(self, request, pk=None):
        """Get AI explanation for parking assignment."""
        assignment = self.get_object()
        
        if assignment.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        engine = ParkingAssignmentEngine()
        explanation = engine.get_assignment_explanation(assignment)
        
        return Response({'explanation': explanation})
    
    @action(detail=True, methods=['POST'])
    def swap_request(self, request, pk=None):
        """Request to swap parking slot with another user."""
        assignment = self.get_object()
        target_user_id = request.data.get('target_user_id')
        
        if assignment.user != request.user:
            return Response(
                {'error': 'Can only request swap for your own assignment.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Logic for swap would be implemented here
        return Response({'message': 'Swap request sent.'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'])
    def complete_assignment(self, request, pk=None):
        """
        Complete a parking assignment and release the slot.
        User can call this when leaving the parking lot early.
        """
        assignment = self.get_object()
        
        # Check permission - user can only complete their own, staff can complete any
        if assignment.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if already completed/cancelled
        if assignment.status != 'active':
            return Response(
                {'error': f'Assignment is already {assignment.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Release the parking slot
        if assignment.parking_slot:
            assignment.parking_slot.status = 'available'
            assignment.parking_slot.save()
        
        # Mark assignment as completed
        assignment.status = 'completed'
        assignment.save()
        
        # Create notification
        from .models import Notification
        Notification.objects.create(
            user=assignment.user,
            title='Parking Assignment Completed',
            message=f'You have successfully completed your parking assignment for {assignment.schedule.title}.',
            notification_type='change',
            priority='medium',
            related_assignment=assignment
        )
        
        return Response(
            {
                'message': 'Assignment completed and slot released.',
                'assignment': AssignmentSerializer(assignment).data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['POST'])
    def confirm_arrival(self, request, pk=None):
        """
        Confirm user arrival at parking lot.
        Must be called within 30-minute grace period after assignment creation.
        """
        assignment = self.get_object()
        
        # Check permission
        if assignment.user != request.user:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if already confirmed
        if assignment.is_confirmed:
            return Response(
                {'error': 'Arrival already confirmed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if past confirmation deadline
        from django.utils import timezone
        if timezone.now() > assignment.confirmation_deadline:
            # Auto-release the slot
            if assignment.parking_slot:
                assignment.parking_slot.status = 'available'
                assignment.parking_slot.save()
            
            assignment.status = 'no_show'
            assignment.save()
            
            # Create no-show record
            from .models import NoShowTracking
            NoShowTracking.objects.create(
                user=assignment.user,
                assignment=assignment,
                was_notified=True
            )
            
            # Notify user
            from .models import Notification
            Notification.objects.create(
                user=assignment.user,
                title='Grace Period Expired',
                message=(
                    f'Your confirmation deadline for {assignment.schedule.title} has expired. '
                    f'The parking slot has been released. This counts as a no-show.'
                ),
                notification_type='alert',
                priority='high',
                related_assignment=assignment
            )
            
            return Response(
                {
                    'error': 'Confirmation deadline has passed. Slot released.',
                    'message': 'This incident has been recorded as a no-show.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Confirm arrival
        assignment.is_confirmed = True
        assignment.confirmed_at = timezone.now()
        assignment.save()
        
        # Create notification
        from .models import Notification
        Notification.objects.create(
            user=assignment.user,
            title='Parking Arrival Confirmed',
            message=(
                f'Your arrival at parking lot {assignment.parking_slot.parking_lot.name}, '
                f'Slot {assignment.parking_slot.slot_number} has been confirmed.'
            ),
            notification_type='change',
            priority='medium',
            related_assignment=assignment
        )
        
        return Response(
            {
                'message': 'Arrival confirmed successfully.',
                'assignment': AssignmentSerializer(assignment).data
            },
            status=status.HTTP_200_OK
        )


class NotificationViewSet(viewsets.ModelViewSet):
    """
    Notification viewset for user notifications.
    Alerts users about assignments, changes, and system events.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('notification_type', 'priority', 'is_read')
    ordering_fields = ('created_at', 'priority')
    
    def get_queryset(self):
        """Filter notifications by current user."""
        if self.request.user.is_staff:
            return Notification.objects.all()
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['GET'])
    def unread(self, request):
        """Get unread notifications."""
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return Response(
            {'message': 'Notification marked as read.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['POST'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for current user."""
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response(
            {'message': 'All notifications marked as read.'},
            status=status.HTTP_200_OK
        )


class AssignmentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Assignment History viewset for audit trail.
    Read-only view of assignment changes and modifications.
    """
    queryset = AssignmentHistory.objects.all()
    serializer_class = AssignmentHistorySerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('assignment',)
    ordering_fields = ('created_at',)
    
    def get_queryset(self):
        """Filter history by user's assignments if not admin."""
        if self.request.user.is_staff:
            return AssignmentHistory.objects.all()
        return AssignmentHistory.objects.filter(assignment__user=self.request.user)
