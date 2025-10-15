# MindMate: Mental Wellness Companion

## Project Overview

MindMate is a comprehensive web-based platform designed to support mental wellness and balance. It provides users with tools for mood tracking, stress detection, guided meditation, exercise recommendations, dietary advice, and access to mental health resources. The platform also includes an admin dashboard for managing users, feedback, and analytics.

The application consists of:
- **Frontend**: A responsive static website built with HTML, CSS, and JavaScript
- **Backend**: A REST API built with FastAPI and SQLAlchemy, using SQLite for data storage

## Frontend Architecture

The frontend is a multi-page static website with the following key pages:

- **index.html**: Homepage with login/signup forms and hero section
- **about.html**: Information about the platform's mission, vision, and values
- **services.html**: Overview of available services (mood tracker, stress detection, meditation, etc.)
- **therapist.html**: Therapist finder functionality
- **testimonials.html**: User testimonials and feedback
- **contact.html**: Contact form and information
- **meditation.html**: Guided meditation sessions
- **mood.html**: Mood tracking interface
- **stress.html**: Stress detection tool
- **exercises.html**: Mental wellness exercises
- **diet.html**: Dietary recommendations for mental health
- **admin.html**: Admin dashboard for managing the platform

### Authentication Flow

The frontend handles user authentication using a combination of client-side storage and API calls:

1. **Registration/Login Forms**: Located on the homepage (index.html)
2. **Client-Side Storage**: User tokens are stored in `localStorage` after successful authentication
3. **Protected Routes**: Certain pages (services, therapist, testimonials, contact) require login
4. **Admin Access**: Separate admin login popup for administrators

### Key Frontend Features

- Responsive design using CSS Grid and Flexbox
- Interactive elements with JavaScript (form validation, API calls)
- Local storage for session management
- Real-time feedback and alerts
- Navigation between pages with authentication checks

## Backend Architecture

The backend is built with FastAPI, providing a RESTful API for all platform functionality.

### Database Models

- **User**: Stores user email and password
- **Feedback**: User feedback with name, country, message, and rating
- **Exercise**: Mental wellness exercises
- **Diet**: Dietary recommendations
- **Video**: Video resources
- **StressResult**: Stress detection results and analysis
- **Admin**: Administrator accounts

### API Endpoints

#### Authentication
- `POST /register`: User registration
- `POST /login`: User login
- `POST /logout`: User logout
- `POST /admin/login`: Admin login
- `POST /admin/logout`: Admin logout

#### Core Features
- `POST /stress`: Stress detection analysis
- `GET /stress/history`: Get user's stress history
- `DELETE /stress/history/delete/{id}`: Delete stress record
- `POST /feedback`: Submit feedback
- `GET /feedback`: Get all feedback

#### Admin Management
- `GET /admin/users`: List all users
- `DELETE /admin/users/{user_id}`: Delete user
- `GET /admin/feedbacks`: List all feedback
- `DELETE /admin/feedbacks/{fid}`: Delete feedback
- `GET /admin/analytics/users`: Get user statistics

## Login Flow Explanation

The login system works as follows:

### User Login Process

1. **Frontend Form Submission**:
   - User enters email and password on the homepage
   - JavaScript validates input (email format, password length)
   - Form data is sent via POST to `/login` endpoint

2. **Backend Authentication**:
   - FastAPI receives the request
   - Queries the database for user with matching email and password
   - If found, generates a secure random token using `secrets.token_hex(16)`
   - Stores token in memory (`user_tokens` dictionary) mapping token to email
   - Returns success response with token

3. **Frontend Token Handling**:
   - Receives token from API response
   - Stores user data (email, token) in `localStorage`
   - Updates UI to show logout option and hide login/signup links
   - Redirects to about.html

4. **Subsequent Requests**:
   - For protected endpoints, frontend includes token in Authorization header
   - Backend validates token against `user_tokens` dictionary
   - If valid, allows access; otherwise returns 401 Unauthorized

5. **Logout**:
   - Frontend sends POST to `/logout` with token
   - Backend removes token from `user_tokens`
   - Frontend clears `localStorage` and updates UI

### Admin Login Process

Similar to user login but:
- Uses `/admin/login` endpoint
- Validates against Admin table
- Stores admin token in `admin_tokens` dictionary
- Grants access to admin-specific endpoints

### Security Considerations

- Passwords stored in plain text (for demo purposes; should use hashing in production)
- Tokens are random hex strings, stored in memory (not persistent across restarts)
- CORS enabled for frontend-backend communication
- Email validation (must be @gmail.com for registration)

## Stress Detection Logic

The stress detection feature analyzes user-inputted vital signs to determine stress levels and provide medical advice.

### Input Parameters
- Blood Pressure (systolic/diastolic, e.g., "120/80")
- Sleep hours (0-24)
- Respiration rate (breaths per minute, 0-60)
- Heart rate (bpm, 0-300)

### Algorithm Steps

1. **Blood Pressure Analysis**:
   - Parse BP string into systolic and diastolic values
   - Determine hypertension stage:
     - Normal: <120/<80
     - Elevated: 120-129/<80
     - Stage 1: 130-139/80-89
     - Stage 2: 140-179/90-119
     - Crisis: ≥180/≥120

2. **Scoring System**:
   - Sleep: <5 hours = +4, <7 hours = +2
   - Heart Rate: >100 bpm = +3, <60 bpm = +2
   - Respiration: >20 or <12 = +2 each

3. **Stress Level Determination**:
   - Score ≥8: HIGH
   - Score ≥5: MEDIUM
   - Score ≥2: LOW
   - Score <2: OPTIMAL

4. **Medical Advice Generation**:
   - Provides stage-specific recommendations
   - Warns for critical values
   - Gives general health tips

### Output
- Stress level (HIGH/MEDIUM/LOW/OPTIMAL)
- Detailed advice text
- BP stage and risk level
- Timestamped record stored in database

## Key Features

1. **User Authentication**: Secure login/signup with token-based sessions
2. **Stress Detection**: AI-powered analysis of vital signs
3. **Mood Tracking**: Daily mood logging and visualization
4. **Guided Meditation**: Relaxation sessions
5. **Exercise & Diet Recommendations**: Mental health-focused activities
6. **Feedback System**: User reviews and ratings
7. **Admin Dashboard**: User management and analytics
8. **Responsive Design**: Works on desktop and mobile devices

## How to Run

### Prerequisites
- Python 3.8+
- pip

### Backend Setup
```bash
cd mindmate-backend
pip install -r requirements.txt
python main.py
```
The API will run on http://127.0.0.1:8000

### Frontend Setup
- Open index.html in a web browser
- Or serve with a local server (e.g., `python -m http.server 3000`)

### Admin Setup
- Run `python create_admin.py` to create an admin account
- Login via the admin popup on the homepage

## Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Styling**: Custom CSS with responsive design
- **Icons/Images**: Local assets and emojis

## Future Enhancements

- Implement secure password hashing
- Add JWT tokens with expiration
- Integrate with external APIs (weather, news)
- Add real-time chat with therapists
- Implement push notifications
- Add data visualization for analytics

---

MindMate aims to make mental wellness accessible and manageable for everyone through technology and compassionate design.
