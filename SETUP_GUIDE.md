# SpotLight - Complete Project Setup Guide

## 🎉 Project Complete!

Your complete **SpotLight Campus Parking Management System** has been created with a full production-ready architecture. Here's everything you need to know to get started.

## 📁 Project Structure

```
Spotlight/
├── backend/                           # Django REST API
│   ├── spotlight_project/            # Main Django project
│   │   ├── settings.py               # Configuration
│   │   ├── urls.py                   # URL routing
│   │   └── wsgi.py                   # WSGI app
│   ├── users_app/                    # User management
│   │   ├── models.py                 # User, Student, Employee, Subscription
│   │   ├── views.py                  # API endpoints
│   │   ├── serializers.py            # Data validation
│   │   └── urls.py
│   ├── parking_app/                  # Parking system
│   │   ├── models.py                 # Campus, Building, Lot, Slot, Assignment
│   │   ├── views.py                  # Parking API endpoints
│   │   ├── serializers.py            # Parking data validation
│   │   ├── assignment_engine.py      # Smart assignment algorithm
│   │   └── urls.py
│   ├── manage.py                     # Django CLI
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Docker container config
│   ├── .env.example                  # Environment template
│   └── README.md
│
├── frontend/                          # React Application
│   ├── src/
│   │   ├── pages/                    # Page components
│   │   │   ├── LoginPage.js
│   │   │   ├── RegisterPage.js
│   │   │   ├── DashboardPage.js
│   │   │   ├── SchedulesPage.js
│   │   │   ├── AssignmentsPage.js
│   │   │   ├── NotificationsPage.js
│   │   │   └── ProfilePage.js
│   │   ├── components/               # Reusable components
│   │   │   ├── Navbar.js
│   │   │   └── ProtectedRoute.js
│   │   ├── services/                 # API services
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   └── parkingService.js
│   │   ├── App.js                    # Main app component
│   │   └── index.js                  # Entry point
│   ├── public/                       # Static files
│   │   └── index.html
│   ├── package.json                  # Dependencies
│   ├── Dockerfile                    # Docker config
│   ├── vercel.json                   # Vercel config
│   ├── .env.example                  # Environment template
│   └── README.md
│
├── docker-compose.yml                # Docker Compose setup
├── .github/
│   └── workflows/
│       └── ci-cd.yml                 # GitHub Actions
├── README.md                          # Main documentation
├── PROJECT_CHECKLIST.md               # Completion status
└── SETUP_GUIDE.md                     # This file
```

## 🚀 Quick Start (5 Minutes)

### Option 1: Backend Only (For Testing)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (uses SQLite by default)
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver

# Access:
# - API: http://localhost:8000/api/
# - Admin: http://localhost:8000/admin/
# - Docs: http://localhost:8000/api/docs/
```

### Option 2: Frontend Only (For Testing)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Open http://localhost:3000
# Login with credentials you create in backend
```

### Option 3: Full Stack (Docker)

```bash
# From project root
docker-compose up

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Database: PostgreSQL on port 5432
```

## 🔑 Key Features Implemented

### ✅ User Management
- User registration (students & employees)
- JWT authentication
- Profile management
- Vehicle information
- Subscription plans

### ✅ Parking System
- Campus/Building management
- Parking lot tracking
- Slot availability
- Multiple slot types (regular, premium, reserved, handicap)

### ✅ Smart Assignment Algorithm
The system automatically assigns the BEST parking slot based on:
1. **Distance** - Closest to your destination (30%)
2. **Lot Type** - Garage > Covered > Outdoor (20%)
3. **Slot Type** - Premium for VIP users (20%)
4. **Occupancy** - Prefer less crowded lots (20%)
5. **User History** - Popular slots for regular users (10%)

### ✅ Schedule Management
- Create class/work schedules
- Recurring schedule support
- Building association
- Time and date ranges

### ✅ Notifications
- Assignment confirmations
- Schedule changes
- Slot availability offers
- Read/unread tracking

### ✅ API Documentation
- Swagger/OpenAPI docs at `/api/docs/`
- RESTful endpoints
- Proper error handling
- Pagination and filtering

## 📊 Database Models

### Users
```
User
├── Student (extends User)
│   ├── student_id
│   ├── major
│   └── campus_building
└── Employee (extends User)
    ├── employee_id
    ├── department
    └── office_building

Subscription
├── user
├── tier (basic/premium/vip)
└── status (active/inactive)
```

### Parking
```
Campus
└── Buildings
    └── ParkingLots
        └── ParkingSlots (individual spaces)

Schedule (User's classes/work)
└── Assignment (Parking slot assigned)
    └── AssignmentHistory (audit trail)
```

## 🔐 API Endpoints (40+)

### Authentication
- `POST /api/auth/register/` - Register
- `POST /api/auth/login/` - Login
- `GET/PUT /api/auth/profile/` - Profile

### Parking
- `GET /api/campus/` - All campuses
- `GET /api/buildings/` - All buildings
- `GET /api/parking-lots/` - Parking lots
- `GET /api/parking-slots/` - Parking slots
- `GET /api/parking-slots/available_slots/` - Available slots

### Schedules
- `GET/POST /api/schedules/` - User schedules
- `POST /api/schedules/{id}/assign_parking/` - Auto assign parking

### Assignments
- `GET /api/assignments/` - User assignments
- `GET /api/assignments/current_assignment/` - Current active
- `POST /api/assignments/{id}/explain/` - AI explanation

### Notifications
- `GET /api/notifications/` - All notifications
- `GET /api/notifications/unread/` - Unread only
- `POST /api/notifications/{id}/mark_as_read/` - Mark as read

### Users
- `GET/POST /api/students/` - Student profiles
- `GET/POST /api/employees/` - Employee profiles
- `GET/POST /api/subscriptions/` - Subscriptions

## 🔧 Configuration

### Backend Environment (.env)

Create `/backend/.env`:

```
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (uses SQLite by default, uncomment for PostgreSQL)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=spotlight_db
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432

# Frontend CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000

# AWS S3 (optional)
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_STORAGE_BUCKET_NAME=spotlight-parking
```

### Frontend Environment (.env)

Create `/frontend/.env`:

```
REACT_APP_API_URL=http://localhost:8000/api
```

## 🚢 Deployment

### Deploy Backend to Render

1. Push to GitHub
2. Create new Web Service on render.com
3. Connect your repository
4. Set environment variables
5. Add PostgreSQL database
6. Deploy!

### Deploy Frontend to Vercel

1. Push to GitHub
2. Import project to vercel.com
3. Set `REACT_APP_API_URL` environment variable
4. Deploy!

### Deploy with Docker

```bash
# Build images
docker build -t spotlight-backend ./backend
docker build -t spotlight-frontend ./frontend

# Run with Docker Compose
docker-compose up -d

# Or push to container registry (Docker Hub, AWS ECR, etc.)
docker tag spotlight-backend yourusername/spotlight-backend
docker push yourusername/spotlight-backend
```

## 📝 Development Workflow

### Backend Development

```bash
cd backend

# Activate virtual environment
source venv/Scripts/activate

# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create test data
python manage.py shell
>>> from users_app.models import User
>>> User.objects.create_user(username='test', password='test')

# Run tests
python manage.py test

# Start server
python manage.py runserver
```

### Frontend Development

```bash
cd frontend

# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test

# Format code
npm run format
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test                    # All tests
python manage.py test parking_app        # Specific app
python manage.py test parking_app.tests  # Specific test
```

### Frontend Tests
```bash
cd frontend
npm test                                 # Run tests
npm test -- --coverage                   # With coverage
npm run build                            # Build test
```

## 📚 API Example Usage

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "student"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

### Create Schedule
```bash
curl -X POST http://localhost:8000/api/schedules/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_type": "class",
    "title": "CS 101 Lecture",
    "building": 1,
    "start_time": "09:00",
    "end_time": "10:30",
    "days_of_week": "Monday,Wednesday,Friday",
    "start_date": "2024-01-15",
    "end_date": "2024-05-15"
  }'
```

### Assign Parking
```bash
curl -X POST http://localhost:8000/api/schedules/1/assign_parking/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Delete old database and migrations
rm db.sqlite3
rm -rf parking_app/migrations/
rm -rf users_app/migrations/

# Run migrations again
python manage.py makemigrations
python manage.py migrate
```

### Frontend can't connect to backend
1. Make sure backend is running: `http://localhost:8000`
2. Check `.env` has correct `REACT_APP_API_URL`
3. Check CORS settings in Django settings.py
4. Open browser console (F12) for network errors

### Port already in use
```bash
# Backend (port 8000)
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows
# Kill process: kill -9 <PID>

# Frontend (port 3000)
lsof -i :3000  # Mac/Linux
netstat -ano | findstr :3000  # Windows
```

## 📖 Documentation

- [Main README](./README.md) - Project overview
- [Backend README](./backend/README.md) - Backend setup
- [Frontend README](./frontend/README.md) - Frontend setup
- [API Docs](http://localhost:8000/api/docs/) - Interactive API documentation
- [Project Checklist](./PROJECT_CHECKLIST.md) - Completion status

## 🎓 Learning Resources

### Django
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Models](https://docs.djangoproject.com/en/stable/topics/db/models/)

### React
- [React Documentation](https://react.dev/)
- [React Router](https://reactrouter.com/)
- [React Hooks](https://react.dev/reference/react/hooks)

### PostgreSQL
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [psycopg2 (Python Driver)](https://www.psycopg.org/)

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/feature-name`
2. Commit changes: `git commit -am 'Add feature'`
3. Push branch: `git push origin feature/feature-name`
4. Create Pull Request on GitHub

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Read the documentation files
3. Check API documentation at `/api/docs/`
4. Review code comments and docstrings

## ✨ Next Steps

1. **Local Testing**
   - Start backend: `python manage.py runserver`
   - Start frontend: `npm start`
   - Test user registration and parking assignment

2. **Database Setup**
   - Install PostgreSQL locally
   - Update `.env` with PostgreSQL credentials
   - Run migrations with PostgreSQL

3. **Add Sample Data**
   - Create campuses and buildings
   - Create parking lots and slots
   - Create test users

4. **Customize**
   - Update colors and branding
   - Add your campus information
   - Customize parking assignment algorithm

5. **Deploy**
   - Push to GitHub
   - Deploy backend to Render
   - Deploy frontend to Vercel

## 🎯 Project Goals Achieved

✅ Full-stack web application
✅ RESTful API design
✅ JWT authentication
✅ Database modeling
✅ Responsive UI
✅ AI-assisted logic
✅ Docker containerization
✅ CI/CD automation
✅ API documentation
✅ Production-ready code

---

## 🚀 You're Ready!

Your SpotLight application is complete and ready to run. Start with the Quick Start guide above and explore the features!

**Questions?** Check the README files or API docs at `/api/docs/`

**Happy coding!** 🎉
