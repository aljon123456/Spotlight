"""
File upload views for S3 integration.
Handles profile picture, document, and video uploads.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import os
import boto3


class FileUploadViewSet(viewsets.ViewSet):
    """ViewSet for handling file uploads to S3."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_s3_client(self):
        """Get boto3 S3 client for pre-signed URLs."""
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
    
    def generate_presigned_url(self, key, expiration=86400):
        """Generate a pre-signed URL for S3 object access (valid 24 hours)."""
        try:
            s3_client = self.get_s3_client()
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': key
                },
                ExpiresIn=expiration
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
            return None
    
    @action(detail=False, methods=['post'])
    def upload_profile_picture(self, request):
        """
        Upload a user's profile picture.
        
        Expected form data:
        - file: Image file (jpg, jpeg, png, webp)
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        # Validate file type
        valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
        file_ext = os.path.splitext(file.name)[1].lstrip('.').lower()
        if file_ext not in valid_extensions:
            return Response(
                {'error': f'Invalid file type. Allowed: {", ".join(valid_extensions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (5MB max)
        if file.size > 5242880:  # 5MB
            return Response(
                {'error': 'File size exceeds 5MB limit'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Update user profile picture
            request.user.profile_picture = file
            request.user.save()
            
            # Generate pre-signed URL for secure access (24 hour expiration)
            s3_key = str(request.user.profile_picture)
            presigned_url = self.generate_presigned_url(s3_key, expiration=86400)
            
            # If pre-signed URL generation fails, try regular URL
            if not presigned_url:
                presigned_url = request.user.profile_picture.url
            
            return Response(
                {
                    'message': 'Profile picture uploaded successfully',
                    'url': presigned_url
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def upload_schedule_document(self, request):
        """
        Upload a schedule document (syllabus, schedule PDF, etc).
        
        Expected form data:
        - file: PDF file
        - schedule_id: ID of the schedule to attach the document to
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'schedule_id' not in request.data:
            return Response(
                {'error': 'schedule_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        schedule_id = request.data.get('schedule_id')
        
        # Validate file type
        valid_extensions = ['pdf', 'jpg', 'jpeg', 'png']
        file_ext = os.path.splitext(file.name)[1].lstrip('.').lower()
        if file_ext not in valid_extensions:
            return Response(
                {'error': f'Invalid file type. Allowed: {", ".join(valid_extensions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (5MB max)
        if file.size > 5242880:  # 5MB
            return Response(
                {'error': 'File size exceeds 5MB limit'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from parking_app.models import Schedule
            
            # Get the schedule
            schedule = Schedule.objects.get(id=schedule_id, user=request.user)
            
            # Upload document
            schedule.schedule_document = file
            schedule.save()
            
            # Generate pre-signed URL
            s3_key = str(schedule.schedule_document)
            presigned_url = self.generate_presigned_url(s3_key, expiration=86400)
            
            if not presigned_url:
                presigned_url = schedule.schedule_document.url
            
            return Response(
                {
                    'message': 'Document uploaded successfully',
                    'url': presigned_url
                },
                status=status.HTTP_200_OK
            )
        except Schedule.DoesNotExist:
            return Response(
                {'error': 'Schedule not found or unauthorized'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def delete_profile_picture(self, request):
        """Delete user's profile picture."""
        try:
            if request.user.profile_picture:
                request.user.profile_picture.delete()
                request.user.profile_picture = None
                request.user.save()
                
                return Response(
                    {'message': 'Profile picture deleted successfully'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'No profile picture to delete'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def get_s3_config(self, request):
        """Get S3 configuration for frontend (non-sensitive)."""
        return Response(
            {
                'bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'region': settings.AWS_S3_REGION_NAME,
                'cdn_domain': settings.AWS_S3_CUSTOM_DOMAIN,
                'media_url': settings.MEDIA_URL,
                'configured': bool(settings.AWS_ACCESS_KEY_ID),
            },
            status=status.HTTP_200_OK
        )
