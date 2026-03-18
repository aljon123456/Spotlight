import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

from users_app.models import User

try:
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123',
        user_type='employee'
    )
    print("✓ Admin account created!")
    print(f"  Username: admin")
    print(f"  Password: admin123")
    print(f"  Email: admin@test.com")
except Exception as e:
    if "already exists" in str(e):
        print("✓ Admin account already exists")
        print(f"  Username: admin")
        print(f"  Password: admin123 (if this was the password set)")
    else:
        print(f"Error: {e}")
