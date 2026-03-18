import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

from users_app.models import User

try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    print("✓ Admin password reset!")
    print(f"  Username: admin")
    print(f"  Password: admin123")
    print(f"\nGo to: http://localhost:8000/admin")
except User.DoesNotExist:
    print("Admin user not found")
