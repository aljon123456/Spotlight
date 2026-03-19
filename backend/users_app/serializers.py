"""
Serializers for User, Student, Employee, and Subscription models.
Handles serialization/deserialization and validation.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Student, Employee, Subscription


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with comprehensive fields."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'password', 'confirm_password',
            'user_type', 'phone_number', 'vehicle_plate', 'vehicle_type', 'profile_picture',
            'is_email_verified', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'is_email_verified')
    
    def validate(self, data):
        """Validate password match and user type."""
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if data.get('user_type') not in ['student', 'employee']:
            raise serializers.ValidationError({"user_type": "Invalid user type."})
        return data
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model with user information."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = ('id', 'user', 'student_id', 'major', 'year', 'gpa', 'campus_building', 'created_at')
        read_only_fields = ('id', 'created_at', 'user')


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model with user information."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Employee
        fields = (
            'id', 'user', 'employee_id', 'department', 'position',
            'office_building', 'office_number', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'user')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = (
            'id', 'user', 'subscription_type', 'status', 'start_date',
            'end_date', 'price', 'is_auto_renew', 'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'start_date')
    
    def get_is_active(self, obj):
        """Get active status of subscription."""
        return obj.is_active()


class LoginSerializer(serializers.Serializer):
    """Serializer for user login with credentials."""
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, data):
        """Authenticate user with username and password."""
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile update with full user data."""
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'phone_number',
            'vehicle_plate', 'vehicle_type', 'profile_picture', 'profile_picture_url', 'user_type'
        )
        read_only_fields = ('id', 'username', 'user_type', 'profile_picture_url')
    
    def get_profile_picture_url(self, obj):
        """Generate pre-signed URL for profile picture."""
        if not obj.profile_picture:
            return None
        
        try:
            import boto3
            from django.conf import settings
            
            if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
                return obj.profile_picture.url
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Generate pre-signed URL
            s3_key = str(obj.profile_picture)
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': s3_key
                },
                ExpiresIn=86400  # 24 hours
            )
            
            # If CloudFront domain is configured, replace S3 domain with CloudFront domain
            if hasattr(settings, 'AWS_CLOUDFRONT_DOMAIN') and settings.AWS_CLOUDFRONT_DOMAIN:
                # Try both formats (with and without region)
                s3_domain_with_region = f'{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com'
                s3_domain_without_region = f'{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
                if s3_domain_with_region in url:
                    url = url.replace(s3_domain_with_region, settings.AWS_CLOUDFRONT_DOMAIN)
                elif s3_domain_without_region in url:
                    url = url.replace(s3_domain_without_region, settings.AWS_CLOUDFRONT_DOMAIN)
            
            return url
        except Exception as e:
            # Fallback to regular URL
            return obj.profile_picture.url
    
    def update(self, instance, validated_data):
        """Update user profile with file handling."""
        # Handle profile picture
        if 'profile_picture' in validated_data:
            profile_picture = validated_data.pop('profile_picture')
            if profile_picture:
                instance.profile_picture = profile_picture
            elif profile_picture is None:
                instance.profile_picture = None
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
