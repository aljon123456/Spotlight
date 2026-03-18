"""
Views for user authentication, profile management, and subscriptions.
Includes registration, login, profile updates, and subscription management.
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Student, Employee, Subscription
from .serializers import (
    UserSerializer, StudentSerializer, EmployeeSerializer,
    SubscriptionSerializer, LoginSerializer, UserProfileSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint.
    Allows new students and employees to create accounts.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    
    def create(self, request, *args, **kwargs):
        """Create new user account and return tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """
    User login endpoint.
    Authenticates user and returns JWT tokens.
    """
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    
    def post(self, request):
        """Authenticate user and generate tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    User profile endpoint.
    Retrieve, update, or delete user profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_object(self):
        """Get current authenticated user."""
        return self.request.user
    
    def destroy(self, request, *args, **kwargs):
        """Deactivate user account instead of deleting."""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(
            {'message': 'Account deactivated successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )


class StudentViewSet(viewsets.ModelViewSet):
    """
    Student profile viewset.
    CRUD operations for student profiles.
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Filter students by user if requested."""
        if self.request.query_params.get('user_id'):
            return Student.objects.filter(user_id=self.request.query_params.get('user_id'))
        return super().get_queryset()
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def my_profile(self, request):
        """Get current student's profile."""
        try:
            student = Student.objects.get(user=request.user)
            serializer = self.get_serializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Employee profile viewset.
    CRUD operations for employee profiles.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Filter employees by user if requested."""
        if self.request.query_params.get('user_id'):
            return Employee.objects.filter(user_id=self.request.query_params.get('user_id'))
        return super().get_queryset()
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def my_profile(self, request):
        """Get current employee's profile."""
        try:
            employee = Employee.objects.get(user=request.user)
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    Subscription viewset.
    Manage user subscriptions for priority parking.
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Filter subscriptions by user if requested."""
        if self.request.query_params.get('user_id'):
            return Subscription.objects.filter(user_id=self.request.query_params.get('user_id'))
        return super().get_queryset()
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def my_subscription(self, request):
        """Get current user's subscription."""
        try:
            subscription = Subscription.objects.get(user=request.user)
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'No active subscription found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def upgrade(self, request):
        """Upgrade user subscription to a higher tier."""
        subscription_type = request.data.get('subscription_type')
        
        if subscription_type not in ['basic', 'premium', 'vip']:
            return Response(
                {'error': 'Invalid subscription type.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscription = Subscription.objects.get(user=request.user)
            subscription.subscription_type = subscription_type
            subscription.status = 'active'
            subscription.save()
            
            return Response(
                {'message': 'Subscription upgraded successfully.', 'subscription': SubscriptionSerializer(subscription).data},
                status=status.HTTP_200_OK
            )
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'Subscription not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
