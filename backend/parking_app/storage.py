"""
Custom storage backends for AWS S3 with different cache settings per file type.
Since the bucket has ACLs disabled and Block Public Access enabled, we use pre-signed URLs.
"""
from storages.backends.s3boto3 import S3Boto3Storage


class ProfilePictureStorage(S3Boto3Storage):
    """Storage for user profile pictures with pre-signed URLs."""
    location = 'profile-pictures'
    default_acl = None  # No ACL (bucket policy handles access)
    
    def get_object_parameters(self, name):
        params = super().get_object_parameters(name)
        params['CacheControl'] = 'max-age=2592000'  # 30 days
        return params
    
    def url(self, name):
        """Generate pre-signed URL for secure access."""
        if not name:
            return ''
        # Generate URL valid for 24 hours
        return self.connection.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': self.location + '/' + name},
            ExpiresIn=86400  # 24 hours
        )


class DocumentStorage(S3Boto3Storage):
    """Storage for documents with pre-signed URLs."""
    location = 'documents'
    default_acl = None
    
    def get_object_parameters(self, name):
        params = super().get_object_parameters(name)
        params['CacheControl'] = 'max-age=604800'  # 7 days
        return params
    
    def url(self, name):
        """Generate pre-signed URL for secure access."""
        if not name:
            return ''
        return self.connection.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': self.location + '/' + name},
            ExpiresIn=86400  # 24 hours
        )


class VideoStorage(S3Boto3Storage):
    """Storage for video files with pre-signed URLs."""
    location = 'videos'
    default_acl = None
    
    def get_object_parameters(self, name):
        params = super().get_object_parameters(name)
        params['CacheControl'] = 'max-age=86400'  # 1 day
        return params
    
    def url(self, name):
        """Generate pre-signed URL for secure access."""
        if not name:
            return ''
        return self.connection.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': self.location + '/' + name},
            ExpiresIn=86400  # 24 hours
        )


class StaticMediaStorage(S3Boto3Storage):
    """Default storage for general media files with pre-signed URLs."""
    location = 'media'
    default_acl = None
    
    def get_object_parameters(self, name):
        params = super().get_object_parameters(name)
        params['CacheControl'] = 'max-age=86400'  # 1 day
        return params
    
    def url(self, name):
        """Generate pre-signed URL for secure access."""
        if not name:
            return ''
        return self.connection.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': self.location + '/' + name},
            ExpiresIn=86400  # 24 hours
        )
