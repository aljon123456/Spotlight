"""
URL configuration for users app.
Routes for authentication, user profiles, students, employees, subscriptions, and payments.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, UserLoginView, UserProfileView,
    StudentViewSet, EmployeeViewSet, SubscriptionViewSet
)
from .payment_views import (
    PaymentPackageViewSet, PaymentViewSet, PaymentInitiateView,
    PaymentExecuteView, PaymentCancelView, SubscriptionInfoView
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'payment-packages', PaymentPackageViewSet, basename='payment-package')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    # Authentication
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    
    # Payments
    path('payments/initiate/', PaymentInitiateView.as_view(), name='payment-initiate'),
    path('payments/execute/', PaymentExecuteView.as_view(), name='payment-execute'),
    path('payments/cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('subscription/current/', SubscriptionInfoView.as_view(), name='subscription-info'),
    
    # Routers
    path('', include(router.urls)),
]
