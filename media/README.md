# Media Files Directory

This directory stores user-uploaded files like images, documents, and other media.

## Directory Structure

```
media/
├── images/          # User profile pictures, ride images, etc.
├── uploads/         # General file uploads
└── README.md        # This file
```

## Usage

### In Django Models
```python
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='images/profiles/')
    
class Ride(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images/rides/')
```

### In Django Views
```python
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        # Save to media/images/
        path = default_storage.save('images/' + image.name, ContentFile(image.read()))
        return JsonResponse({'url': f'/media/{path}'})
```

### Accessing Files
- Local development: `http://localhost:8000/media/images/filename.jpg`
- Production: `https://your-domain.com/media/images/filename.jpg`

## File Organization

### Images
- `images/profiles/` - User profile pictures
- `images/rides/` - Ride-related images
- `images/vehicles/` - Vehicle images
- `images/documents/` - Document images

### Uploads
- `uploads/temp/` - Temporary uploads
- `uploads/documents/` - General documents
- `uploads/backups/` - Backup files

## Security Notes

1. **File Validation**: Always validate file types and sizes
2. **Access Control**: Implement proper permissions for file access
3. **Storage**: Consider using cloud storage (AWS S3, Google Cloud Storage) for production
4. **Cleanup**: Implement cleanup for temporary files

## Production Considerations

For production deployment, consider:

1. **Cloud Storage**: Use AWS S3, Google Cloud Storage, or Azure Blob Storage
2. **CDN**: Use a Content Delivery Network for faster file delivery
3. **Backup**: Implement regular backups of important files
4. **Monitoring**: Monitor storage usage and costs

## Example Configuration for Cloud Storage

```python
# settings.py
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```
