# Campus Event Management Platform
Event_knot

## 🎯 Project Overview

The Campus Event Management Platform is a comprehensive web-based system designed to streamline event management across multiple colleges and universities. The platform serves two primary user groups:

- **Administrators**: College staff who create, manage, and monitor campus events
- **Students**: Campus community members who browse, register for, and participate in events

The system solves the challenge of managing large-scale campus events by providing:
- Centralized event creation and management
- Automated student registration and capacity management
- Real-time attendance tracking with QR code support
- Comprehensive feedback collection and analytics
- Multi-college support with scalable architecture

### Key Features

- **Event Management**: Create, update, and manage campus events
- **Student Registration**: Students can browse and register for events
- **Attendance Tracking**: Check-in/check-out system for event attendance
- **Feedback Collection**: Students can rate and review events
- **Comprehensive Reporting**: Analytics and insights for administrators
- **Multi-College Support**: Manage events across multiple institutions

## 🛠️ Technology Stack

- **Backend**: Python 3.8+ with FastAPI
- **Database**: SQLite 
- **ORM**: SQLAlchemy for database operations
- **Validation**: Pydantic for data validation
- **API Documentation**: Auto-generated with Swagger UI

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Saynsha/Event_knot.git
cd webknot
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
# Start the development server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Application

- **Landing Page**: http://localhost:8000/
- **Admin Portal**: http://localhost:8000/admin
- **Student App**: http://localhost:8000/student
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📊 Database Schema

The platform uses SQLite with the following main entities:

- **Colleges**: Educational institutions
- **Students**: Student records linked to colleges
- **Events**: Campus events with capacity and timing
- **Registrations**: Student event registrations
- **Attendance**: Check-in/check-out records
- **Feedback**: Student ratings and comments

## 🌐 Web Interfaces

### Admin Portal (`/admin`)
- **Dashboard**: Overview of system statistics and recent activity
- **Event Management**: Create, edit, and manage campus events
- **Student Management**: Add and manage student records
- **Attendance Tracking**: Real-time check-in/check-out interface
- **Feedback Management**: View and analyze event feedback
- **Reports & Analytics**: Comprehensive reporting dashboard
- **College Management**: Manage multiple college institutions

### Student App (`/student`)
- **Event Browser**: Search and filter available events
- **Event Registration**: Easy one-click event registration
- **My Events**: View registered and attended events
- **QR Code Check-in**: Generate personal QR code for quick check-in
- **Feedback System**: Rate and review attended events
- **Mobile-Optimized**: Responsive design for mobile devices

### Landing Page (`/`)
- **Interface Selection**: Choose between Admin Portal and Student App
- **System Status**: Real-time system health monitoring
- **API Documentation**: Direct links to API documentation

## 🔌 API Endpoints

### Core Endpoints

#### Colleges
- `POST /colleges/` - Create new college
- `GET /colleges/` - List all colleges
- `GET /colleges/{id}` - Get college details
- `PUT /colleges/{id}` - Update college

#### Students
- `POST /students/` - Add new student
- `GET /students/` - List students (with filters)
- `GET /students/{id}` - Get student details
- `PUT /students/{id}` - Update student

#### Events
- `POST /events/` - Create new event
- `GET /events/` - List events (with filters)
- `GET /events/{id}` - Get event details
- `PUT /events/{id}` - Update event
- `DELETE /events/{id}` - Cancel event

#### Registration
- `POST /register/` - Register student for event
- `GET /register/` - List registrations
- `DELETE /register/{id}` - Cancel registration

#### Attendance
- `POST /attendance/` - Mark attendance (check-in/out)
- `GET /attendance/` - List attendance records

#### Feedback
- `POST /feedback/` - Submit event feedback
- `GET /feedback/` - List feedback records

### Reporting Endpoints

- `GET /reports/registrations/` - Registration statistics
- `GET /reports/attendance/` - Attendance percentages
- `GET /reports/feedback/` - Feedback scores
- `GET /reports/top-students/` - Most active students
- `GET /reports/events/` - Event statistics
- `GET /reports/comprehensive/` - All statistics

## 📝 API Usage Examples

### 1. Create a College

```bash
curl -X POST "http://localhost:8000/colleges/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "University of Technology",
    "location": "New York, NY",
    "contact_email": "admin@university.edu"
  }'
```

### 2. Add a Student

```bash
curl -X POST "http://localhost:8000/students/" \
  -H "Content-Type: application/json" \
  -d '{
    "college_id": 1,
    "student_id": "STU001",
    "name": "John Doe",
    "email": "john.doe@university.edu",
    "phone": "+1-555-0123"
  }'
```

### 3. Create an Event

```bash
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "college_id": 1,
    "title": "Bengaluru Tech Conference 2025",
    "description": "Annual technology conference",
    "event_type": "Conference",
    "start_time": "2024-03-15T09:00:00",
    "end_time": "2024-03-15T17:00:00",
    "location": "Main Auditorium",
    "max_capacity": 200
  }'
```

### 4. Register Student for Event

```bash
curl -X POST "http://localhost:8000/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "event_id": 1
  }'
```

### 5. Mark Attendance (Check-in)

```bash
curl -X POST "http://localhost:8000/attendance/" \
  -H "Content-Type: application/json" \
  -d '{
    "registration_id": 1,
    "action": "check_in"
  }'
```

### 6. Submit Feedback

```bash
curl -X POST "http://localhost:8000/feedback/" \
  -H "Content-Type: application/json" \
  -d '{
    "registration_id": 1,
    "rating": 5,
    "comment": "Excellent event! Very informative."
  }'
```

### 7. Get Registration Statistics

```bash
curl -X GET "http://localhost:8000/reports/registrations/?college_id=1"
```

### 8. Get Top Students

```bash
curl -X GET "http://localhost:8000/reports/top-students/?limit=5"
```

## 🧪 Testing the API

### Using Postman

1. Import the API collection (if available)
2. Set base URL to `http://localhost:8000`
3. Test endpoints in sequence:
   - Create college → Create student → Create event → Register → Attend → Feedback

### Using curl

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API documentation
curl http://localhost:8000/docs
```

## 📁 Project Structure

```
webknot/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   └── reports.py           # Reporting functions
├── design_doc.md            # System design document
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── campus_events.db        # SQLite database (created on first run)
```

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL`: Database connection string (default: `sqlite:///./campus_events.db`)

### Database Configuration

The application uses SQLite by default for simplicity and portability. For production, consider:

- PostgreSQL for better performance
- MySQL for enterprise environments
- Configure connection pooling for high traffic

## 📈 Performance Considerations

- **Database Indexing**: Optimized indexes for common queries
- **Pagination**: All list endpoints support pagination
- **Caching**: Consider Redis for frequently accessed data cause we can acess fastr caching using redic and reduce latency
- **Connection Pooling**: For production database connections

## 🚨 Assumptions & Limitations

### Assumptions Made During Development

- **Student ID Uniqueness**: Student IDs are unique within each college, not same globally
- **Event Capacity**: All events have maximum capacity limits to prevent overcrowding
- **Single Registration**: Students can only register once per event to prevent duplicates
- **Attendance Tracking**: Manual check-in/check-out system with QR code support
- **Feedback Timing**: Feedback can only be submitted by students who attended events
- **Event Status Flow**: Events follow a lifecycle: active → completed/cancelled
- **College Isolation**: Each college manages its own events and students independently
- **Real-time Updates**: Web interfaces update in real-time for better user experience

### System Limitations

- **Database**: SQLite may not scale to very high concurrent users (1000+ simultaneous)
- **Authentication**: No built-in user authentication system (demo mode only)
- **Notifications**: No email/SMS notifications for event reminders
- **Mobile App**: Web-based only, no native mobile applications
- **File Uploads**: No support for event images or document attachments
- **Real-time Chat**: No real-time communication features

### Known Limitations

- SQLite may not scale to very high concurrent users
- No real-time notifications for event updates
- No email integration for event reminders
- No mobile app (web-based only)

## 🔮 Future Enhancements

Potential Future improvements:

- Real-time notifications
- Email integration
- Mobile app development
- Advanced analytics dashboard
- Integration with college management systems
- QR code generation for quick check-ins
