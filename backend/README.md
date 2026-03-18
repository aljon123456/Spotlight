# Backend README
# SpotLight Backend - Django REST API

## Setup

1. Create virtual environment:
   ```
   python -m venv venv
   source venv/Scripts/activate  # Windows
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create superuser:
   ```
   python manage.py createsuperuser
   ```

5. Run development server:
   ```
   python manage.py runserver
   ```

## API Documentation

- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/docs/
- Schema: http://localhost:8000/api/schema/

## Key Endpoints

### Authentication
- POST /api/auth/register/ - Register new user
- POST /api/auth/login/ - Login user
- GET/PUT /api/auth/profile/ - User profile

### Parking
- GET /api/parking-slots/ - List parking slots
- GET /api/assignments/ - List user assignments
- POST /api/schedules/{id}/assign_parking/ - Assign parking

## Environment Variables

Create .env file with:
```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=spotlight_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
ALLOWED_HOSTS=localhost,127.0.0.1
```
