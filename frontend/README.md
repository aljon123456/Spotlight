# Frontend README
# SpotLight Frontend - React Application

## Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Create `.env` file:
   ```
   REACT_APP_API_URL=http://localhost:8000/api
   ```

3. Start development server:
   ```
   npm start
   ```

   The app will open at `http://localhost:3000`

## Features

- **User Authentication**: Login and registration for students and employees
- **Schedule Management**: Create and manage class/work schedules
- **Parking Assignments**: Automatic parking slot assignment based on schedules
- **AI Explanation**: View AI-powered explanations for parking assignments
- **Notifications**: Real-time notifications about parking changes
- **Profile Management**: Update user information and vehicle details

## Key Pages

- `/login` - User login
- `/register` - New user registration
- `/dashboard` - Main dashboard with current assignment
- `/schedules` - Manage class/work schedules
- `/assignments` - View all parking assignments
- `/notifications` - View system notifications
- `/profile` - User profile settings

## API Integration

The frontend communicates with Django REST backend at `http://localhost:8000/api`

Key API endpoints used:
- `POST /auth/register/` - User registration
- `POST /auth/login/` - User authentication
- `GET/PUT /auth/profile/` - User profile
- `GET/POST /schedules/` - Schedule management
- `POST /schedules/{id}/assign_parking/` - Parking assignment
- `GET /assignments/` - View assignments
- `GET /notifications/` - Notifications

## Build for Production

```
npm run build
```

This creates an optimized production build in the `build` folder.

## Technologies Used

- React 18
- React Router
- Axios (HTTP client)
- React Toastify (notifications)
- CSS3 (responsive design)
