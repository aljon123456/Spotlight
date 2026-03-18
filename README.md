# SpotLight - Campus Parking Management System

A smart, web-based parking management system that automatically assigns parking slots to students and employees based on their schedules, building locations, and parking availability.

## 🎯 Project Overview

SpotLight leverages AI-assisted decision logic (rule-based + simulated) to provide:
- **Automatic Parking Assignment**: Slot assignment based on class/work schedules
- **Smart Routing**: Closest available parking to user's destination
- **Priority Parking**: Subscription-based priority slot access
- **Real-time Notifications**: Updates on assignment changes
- **AI Explanations**: Understand why you got assigned a specific slot

## 🏗️ Architecture

### Frontend (React)
- **Location**: `/frontend`
- **Port**: 3000
- Responsive UI for students and employees
- Real-time notifications
- Schedule and assignment management
- User profile management

### Backend (Django REST)
- **Location**: `/backend`
- **Port**: 8000
- RESTful API endpoints
- JWT authentication
- PostgreSQL database
- Parking assignment engine with **advanced algorithms**
- Admin dashboard
- **25 Professional Algorithms** (Sorting, Searching, Graph, Optimization)


### Database (PostgreSQL)
- User profiles (students/employees)
- Campus, buildings, parking lots, and slots
- Schedules and assignments
- Notifications and assignment history
- Subscription information

## 🚀 Quick Start

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Run migrations (SQLite by default, PostgreSQL optional)
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata sample_data.json

# Run development server
python manage.py runserver
```

**Backend runs at**: http://localhost:8000
**Admin**: http://localhost:8000/admin
**API Docs**: http://localhost:8000/api/docs/

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Start development server
npm start
```

**Frontend runs at**: http://localhost:3000

## 📚 API Documentation

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `GET/PUT /api/auth/profile/` - User profile management

### Parking Management
- `GET /api/campus/` - List campuses
- `GET /api/buildings/` - List buildings
- `GET /api/parking-lots/` - List parking lots
- `GET /api/parking-slots/` - List parking slots
- `GET /api/parking-slots/available_slots/` - Get available slots

### Schedules & Assignments
- `GET/POST /api/schedules/` - Manage schedules
- `POST /api/schedules/{id}/assign_parking/` - Assign parking for schedule
- `GET /api/assignments/` - View assignments
- `GET /api/assignments/current_assignment/` - Get current active assignment
- `POST /api/assignments/{id}/explain/` - Get AI explanation

### Notifications
- `GET /api/notifications/` - List notifications
- `GET /api/notifications/unread/` - Get unread notifications
- `POST /api/notifications/{id}/mark_as_read/` - Mark as read

### Users
- `GET/POST /api/students/` - Student profiles
- `GET/POST /api/employees/` - Employee profiles
- `GET/POST /api/subscriptions/` - Manage subscriptions

## 🔑 Key Features

### 1. Smart Parking Assignment
- Rule-based algorithm considers:
  - Distance to destination building
  - Parking lot characteristics (garage, outdoor, etc.)
  - User subscription level
  - Lot occupancy rates
  - Time of day

### 2. Parking Check-In & Auto Release System
- **30-minute grace period** after assignment
- Users confirm arrival with one click
- Automatic slot release if no confirmation
- No-show tracking and accountability
- Transparent fairness without sensors

### 3. AI-Powered Explanations
- Every assignment includes:
  - Why this slot was chosen
  - Confidence score (0-100%)
  - Distance to your class/office
  - Key factors in the decision

### 4. Flexible Scheduling
- Support for recurring schedules
- Multiple buildings and time slots
- Automatic parking reassignment when schedule changes

### 5. Subscription Tiers
- **Basic**: Standard parking access
- **Premium**: Priority parking slots
- **VIP**: Reserved premium spots


### 5. Real-time Notifications
- Assignment confirmations
- Schedule changes
- Available slot offers
- System alerts

## 🏛️ Database Models

### Users & Authentication
- `User`: Extended Django user with parking-specific fields
- `Student`: Student profile with academic info
- `Employee`: Employee profile with department info
- `Subscription`: Subscription plans and status

### Parking Infrastructure
- `Campus`: University campus
- `Building`: Campus buildings (where classes/offices are)
- `ParkingLot`: Parking areas with available slots
- `ParkingSlot`: Individual parking spaces

### Schedules & Assignments
- `Schedule`: User class/work schedules
- `Assignment`: Parking slot assignment to users
- `AssignmentHistory`: Audit trail of assignment changes

### Notifications
- `Notification`: System alerts and updates

## 🔐 Security Features

- JWT Token-based authentication
- CORS enabled for frontend/backend separation
- Password hashing with Django's security tools
- Environment-based configuration
- SQL injection prevention (Django ORM)
- CSRF protection

## 📦 Tech Stack

### Frontend
- React 18
- React Router (navigation)
- Axios (HTTP client)
- React Toastify (notifications)
- CSS3 (responsive design)

### Backend
- Django 4.2
- Django REST Framework
- PostgreSQL (or SQLite for development)
- JWT authentication
- Celery (for async tasks, optional)
- AWS S3 (for file uploads, optional)

### DevOps
- Vercel (frontend deployment)
- Render (backend deployment)
- Docker (optional containerization)

## 🚢 Deployment

### Frontend (Vercel)
1. Push code to GitHub
2. Connect Vercel to repository
3. Set environment variables in Vercel dashboard
4. Deploy automatically on push

### Backend (Render)
1. Create new Web Service on Render
2. Connect GitHub repository
3. Set environment variables
4. Add PostgreSQL database
5. Deploy

## 📋 File Structure

```
Spotlight/
├── backend/
│   ├── spotlight_project/
│   │   ├── settings.py (Django configuration)
│   │   ├── urls.py (URL routing)
│   │   ├── wsgi.py (WSGI application)
│   │   └── __init__.py
│   ├── users_app/
│   │   ├── models.py (User, Student, Employee, Subscription)
│   │   ├── views.py (API endpoints)
│   │   ├── serializers.py (Data validation)
│   │   └── urls.py
│   ├── parking_app/
│   │   ├── models.py (Campus, Building, Lot, Slot, Assignment)
│   │   ├── views.py (Parking API endpoints)
│   │   ├── serializers.py (Parking data validation)
│   │   ├── assignment_engine.py (Smart assignment algorithm)
│   │   └── urls.py
│   ├── manage.py (Django CLI)
│   ├── requirements.txt (Python dependencies)
│   ├── .env.example (Environment template)
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.js
│   │   │   ├── RegisterPage.js
│   │   │   ├── DashboardPage.js
│   │   │   ├── SchedulesPage.js
│   │   │   ├── AssignmentsPage.js
│   │   │   ├── NotificationsPage.js
│   │   │   ├── ProfilePage.js
│   │   │   └── Pages.css
│   │   ├── components/
│   │   │   ├── Navbar.js
│   │   │   ├── Navbar.css
│   │   │   └── ProtectedRoute.js
│   │   ├── services/
│   │   │   ├── api.js (Axios config)
│   │   │   ├── authService.js
│   │   │   └── parkingService.js
│   │   ├── App.js (Main component)
│   │   ├── App.css
│   │   └── index.js (Entry point)
│   ├── public/
│   │   └── index.html
│   ├── package.json (Dependencies)
│   ├── .env.example (Environment template)
│   └── README.md
│
└── README.md (This file)
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=spotlight_db
DB_USER=postgres
DB_PASSWORD=your_password
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

**Frontend (.env)**
```
REACT_APP_API_URL=https://your-api.onrender.com/api
```

## 🧪 Testing

### Backend
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test parking_app

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend
```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## 📊 Assignment Algorithm

The parking assignment engine uses multiple factors:

1. **Distance** (30% weight)
   - Closest parking to destination building

2. **Slot Type** (20% weight)
   - Premium/reserved slots for subscribers

3. **Lot Coverage** (20% weight)
   - Garage/covered preferred over outdoor

4. **Occupancy** (20% weight)
   - Less crowded lots preferred

5. **User History** (10% weight)
   - Popular slots for reliable users

## 🎓 Learning Outcomes

This project demonstrates:
- Full-stack web application development
- RESTful API design and implementation
- React component architecture
- Django ORM and QuerySets
- Authentication and authorization
- Database design and relationships
- Responsive web design
- Git workflow and version control
- Deployment and DevOps basics
- AI/ML simulation (rule-based logic)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💼 Author

Created as an academic project for campus parking management.

## 🆘 Support & Troubleshooting

### Common Issues

**Backend won't start**
- Check PostgreSQL is running: `psql --version`
- Run migrations: `python manage.py migrate`
- Check .env file exists with correct settings

**Frontend can't connect to API**
- Check backend is running on port 8000
- Verify REACT_APP_API_URL in .env
- Check CORS settings in Django settings.py

**Migrations failing**
- Delete `db.sqlite3` and `migrations/` folders (dev only)
- Run: `python manage.py makemigrations && python manage.py migrate`

## 📞 Contact

For questions or issues, please open an issue on GitHub.

---

**Made with ❤️ for smarter campus parking**
