#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

from users_app.models import User

# Delete existing admin if any
User.objects.filter(username='admin').delete()

# Create fresh admin user
admin = User.objects.create_superuser('admin', 'admin@test.com', 'admin123!')
print('✓ Fresh admin user created successfully!')
print(f'✓ Username: admin')
print(f'✓ Password: admin123!')
print(f'✓ Is staff: {admin.is_staff}')
print(f'✓ Is superuser: {admin.is_superuser}')
