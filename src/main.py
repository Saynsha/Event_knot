"""
FastAPI main application for Campus Event Management Platform.
Provides REST API endpoints for event management, student registration, attendance tracking, and reporting.
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn

from .database import get_db, create_tables
from .models import College, Student, Event, Registration, Attendance, Feedback
from .schemas import (
    # College schemas
    CollegeCreate, CollegeUpdate, CollegeResponse,
    # Student schemas
    StudentCreate, StudentUpdate, StudentResponse,
    # Event schemas
    EventCreate, EventUpdate, EventResponse, EventSearchParams,
    # Registration schemas
    RegistrationCreate, RegistrationResponse,
    # Attendance schemas
    AttendanceCreate, AttendanceResponse,
    # Feedback schemas
    FeedbackCreate, FeedbackResponse,
    # Report schemas
    RegistrationStatsResponse, AttendanceStatsResponse, FeedbackStatsResponse,
    StudentStatsResponse, EventStatsResponse, ReportFilters
)
from .reports import ReportGenerator, generate_all_reports

# Create FastAPI app
app = FastAPI(
    title="Campus Event Management Platform",
    description="A comprehensive event management system for colleges with student registration, attendance tracking, and feedback collection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    print("Database tables created successfully!")


# ==================== WEB INTERFACE ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Landing page with interface selection"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard"""
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


@app.get("/student", response_class=HTMLResponse)
async def student_app(request: Request):
    """Student application"""
    return templates.TemplateResponse("student_app.html", {"request": request})


# ==================== HEALTH CHECK ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"message": "Campus Event Management Platform API", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# ==================== COLLEGE ENDPOINTS ====================

@app.post("/colleges/", response_model=CollegeResponse, status_code=status.HTTP_201_CREATED)
async def create_college(college: CollegeCreate, db: Session = Depends(get_db)):
    """Create a new college"""
    db_college = College(**college.dict())
    db.add(db_college)
    db.commit()
    db.refresh(db_college)
    return db_college


@app.get("/colleges/", response_model=List[CollegeResponse])
async def list_colleges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all colleges with pagination"""
    colleges = db.query(College).offset(skip).limit(limit).all()
    return colleges


@app.get("/colleges/{college_id}", response_model=CollegeResponse)
async def get_college(college_id: int, db: Session = Depends(get_db)):
    """Get college by ID"""
    college = db.query(College).filter(College.id == college_id).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    return college


@app.put("/colleges/{college_id}", response_model=CollegeResponse)
async def update_college(college_id: int, college_update: CollegeUpdate, db: Session = Depends(get_db)):
    """Update college information"""
    college = db.query(College).filter(College.id == college_id).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    update_data = college_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(college, field, value)
    
    db.commit()
    db.refresh(college)
    return college


# ==================== STUDENT ENDPOINTS ====================

@app.post("/students/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student"""
    # Check if college exists
    college = db.query(College).filter(College.id == student.college_id).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    # Check for duplicate student_id within college
    existing_student = db.query(Student).filter(
        Student.college_id == student.college_id,
        Student.student_id == student.student_id
    ).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Student ID already exists in this college")
    
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get("/students/", response_model=List[StudentResponse])
async def list_students(
    college_id: Optional[int] = None,
    search_term: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List students with optional filtering"""
    query = db.query(Student)
    
    if college_id:
        query = query.filter(Student.college_id == college_id)
    
    if search_term:
        query = query.filter(
            Student.name.contains(search_term) |
            Student.email.contains(search_term) |
            Student.student_id.contains(search_term)
        )
    
    students = query.offset(skip).limit(limit).all()
    return students


@app.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get student by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    """Update student information"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    return student


# ==================== EVENT ENDPOINTS ====================

@app.post("/events/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new event"""
    # Check if college exists
    college = db.query(College).filter(College.id == event.college_id).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    # Validate event timing
    if event.end_time <= event.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.get("/events/", response_model=List[EventResponse])
async def list_events(
    college_id: Optional[int] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search_term: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List events with optional filtering"""
    query = db.query(Event)
    
    if college_id:
        query = query.filter(Event.college_id == college_id)
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    if status:
        query = query.filter(Event.status == status)
    
    if start_date:
        query = query.filter(Event.start_time >= start_date)
    
    if end_date:
        query = query.filter(Event.end_time <= end_date)
    
    if search_term:
        query = query.filter(
            Event.title.contains(search_term) |
            Event.description.contains(search_term)
        )
    
    events = query.offset(skip).limit(limit).all()
    return events


@app.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.put("/events/{event_id}", response_model=EventResponse)
async def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db)):
    """Update event information"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    return event


@app.delete("/events/{event_id}")
async def cancel_event(event_id: int, db: Session = Depends(get_db)):
    """Cancel an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = "cancelled"
    db.commit()
    return {"message": "Event cancelled successfully"}


# ==================== REGISTRATION ENDPOINTS ====================

@app.post("/register/", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_student(registration: RegistrationCreate, db: Session = Depends(get_db)):
    """Register a student for an event"""
    # Check if student exists
    student = db.query(Student).filter(Student.id == registration.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if event exists and is active
    event = db.query(Event).filter(Event.id == registration.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.status != "active":
        raise HTTPException(status_code=400, detail="Event is not active for registration")
    
    # Check if event is in the future
    if event.start_time <= datetime.now():
        raise HTTPException(status_code=400, detail="Cannot register for past events")
    
    # Check for duplicate registration
    existing_registration = db.query(Registration).filter(
        Registration.student_id == registration.student_id,
        Registration.event_id == registration.event_id
    ).first()
    if existing_registration:
        raise HTTPException(status_code=400, detail="Student already registered for this event")
    
    # Check capacity
    if event.current_registrations >= event.max_capacity:
        raise HTTPException(status_code=400, detail="Event is at full capacity")
    
    # Create registration
    db_registration = Registration(**registration.dict())
    db.add(db_registration)
    
    # Update event registration count
    event.current_registrations += 1
    
    db.commit()
    db.refresh(db_registration)
    return db_registration


@app.get("/register/", response_model=List[RegistrationResponse])
async def list_registrations(
    student_id: Optional[int] = None,
    event_id: Optional[int] = None,
    college_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List registrations with optional filtering"""
    query = db.query(Registration)
    
    if student_id:
        query = query.filter(Registration.student_id == student_id)
    
    if event_id:
        query = query.filter(Registration.event_id == event_id)
    
    if college_id:
        query = query.join(Student).filter(Student.college_id == college_id)
    
    registrations = query.offset(skip).limit(limit).all()
    return registrations


@app.delete("/register/{registration_id}")
async def cancel_registration(registration_id: int, db: Session = Depends(get_db)):
    """Cancel a student registration"""
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Update event registration count
    event = db.query(Event).filter(Event.id == registration.event_id).first()
    if event and event.current_registrations > 0:
        event.current_registrations -= 1
    
    # Update registration status
    registration.status = "cancelled"
    
    db.commit()
    return {"message": "Registration cancelled successfully"}


# Retrieve a single registration by ID (used by student UI)
@app.get("/register/{registration_id}", response_model=RegistrationResponse)
async def get_registration(registration_id: int, db: Session = Depends(get_db)):
    """Get a registration by its ID"""
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    return registration


# ==================== ATTENDANCE ENDPOINTS ====================

@app.post("/attendance/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def mark_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """Mark student attendance (check-in or check-out)"""
    # Find registration
    registration = db.query(Registration).filter(
        Registration.id == attendance.registration_id
    ).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Check if student is registered for the event
    if registration.status != "registered":
        raise HTTPException(status_code=400, detail="Student is not registered for this event")
    
    # Get or create attendance record
    attendance_record = db.query(Attendance).filter(
        Attendance.registration_id == attendance.registration_id
    ).first()
    
    if not attendance_record:
        attendance_record = Attendance(registration_id=attendance.registration_id)
        db.add(attendance_record)
    
    # Handle check-in/check-out
    current_time = datetime.now()
    
    if attendance.action == "check_in":
        if attendance_record.check_in_time:
            raise HTTPException(status_code=400, detail="Student already checked in")
        
        attendance_record.check_in_time = current_time
        attendance_record.status = "present"
        
        # Check if student is late (after event start time)
        event = db.query(Event).filter(Event.id == registration.event_id).first()
        if event and current_time > event.start_time + timedelta(minutes=15):
            attendance_record.status = "late"
    
    elif attendance.action == "check_out":
        if not attendance_record.check_in_time:
            raise HTTPException(status_code=400, detail="Student must check in before checking out")
        
        if attendance_record.check_out_time:
            raise HTTPException(status_code=400, detail="Student already checked out")
        
        attendance_record.check_out_time = current_time
    
    db.commit()
    db.refresh(attendance_record)
    return attendance_record


@app.get("/attendance/", response_model=List[AttendanceResponse])
async def list_attendance(
    event_id: Optional[int] = None,
    student_id: Optional[int] = None,
    college_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List attendance records with optional filtering"""
    query = db.query(Attendance)
    
    if event_id:
        query = query.join(Registration).filter(Registration.event_id == event_id)
    
    if student_id:
        query = query.join(Registration).filter(Registration.student_id == student_id)
    
    if college_id:
        query = query.join(Registration).join(Student).filter(Student.college_id == college_id)
    
    if status:
        query = query.filter(Attendance.status == status)
    
    attendance_records = query.offset(skip).limit(limit).all()
    return attendance_records


# ==================== FEEDBACK ENDPOINTS ====================

@app.post("/feedback/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit event feedback"""
    # Find registration
    registration = db.query(Registration).filter(
        Registration.id == feedback.registration_id
    ).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Check if student attended the event
    attendance = db.query(Attendance).filter(
        Attendance.registration_id == feedback.registration_id,
        Attendance.status.in_(["present", "late"])
    ).first()
    if not attendance:
        raise HTTPException(status_code=400, detail="Only students who attended the event can submit feedback")
    
    # Check if feedback already exists
    existing_feedback = db.query(Feedback).filter(
        Feedback.registration_id == feedback.registration_id
    ).first()
    if existing_feedback:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this event")
    
    db_feedback = Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


@app.get("/feedback/", response_model=List[FeedbackResponse])
async def list_feedback(
    event_id: Optional[int] = None,
    student_id: Optional[int] = None,
    college_id: Optional[int] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List feedback with optional filtering"""
    query = db.query(Feedback)
    
    if event_id:
        query = query.join(Registration).filter(Registration.event_id == event_id)
    
    if student_id:
        query = query.join(Registration).filter(Registration.student_id == student_id)
    
    if college_id:
        query = query.join(Registration).join(Student).filter(Student.college_id == college_id)
    
    if min_rating:
        query = query.filter(Feedback.rating >= min_rating)
    
    if max_rating:
        query = query.filter(Feedback.rating <= max_rating)
    
    feedback_records = query.offset(skip).limit(limit).all()
    return feedback_records


# ==================== REPORTING ENDPOINTS ====================

@app.get("/reports/registrations/")
async def get_registration_stats(
    college_id: Optional[int] = None,
    event_id: Optional[int] = None,
    event_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get registration statistics per event"""
    reporter = ReportGenerator(db)
    
    if event_id:
        # Get specific event stats
        events = db.query(Event).filter(Event.id == event_id).all()
        if not events:
            raise HTTPException(status_code=404, detail="Event not found")
    else:
        # Get all events with filters
        query = db.query(Event)
        if college_id:
            query = query.filter(Event.college_id == college_id)
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if start_date:
            query = query.filter(Event.start_time >= start_date)
        if end_date:
            query = query.filter(Event.end_time <= end_date)
        events = query.all()
    
    stats = []
    for event in events:
        registrations = db.query(Registration).filter(Registration.event_id == event.id).count()
        stats.append({
            "event_id": event.id,
            "event_title": event.title,
            "event_type": event.event_type,
            "start_time": event.start_time,
            "max_capacity": event.max_capacity,
            "current_registrations": event.current_registrations,
            "total_registrations": registrations,
            "registration_percentage": round((event.current_registrations * 100.0 / event.max_capacity), 2)
        })
    
    return {"registration_stats": stats}


@app.get("/reports/attendance/")
async def get_attendance_stats(
    college_id: Optional[int] = None,
    event_id: Optional[int] = None,
    event_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get attendance percentage per event"""
    reporter = ReportGenerator(db)
    stats = reporter.get_attendance_summary_report(college_id)
    
    # Apply additional filters
    if event_id:
        stats = [s for s in stats if s["event_id"] == event_id]
    if event_type:
        stats = [s for s in stats if s["event_type"] == event_type]
    if start_date:
        stats = [s for s in stats if s["start_time"] >= start_date]
    if end_date:
        stats = [s for s in stats if s["start_time"] <= end_date]
    
    return {"attendance_stats": stats}


@app.get("/reports/feedback/")
async def get_feedback_stats(
    college_id: Optional[int] = None,
    event_id: Optional[int] = None,
    event_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get average feedback score per event"""
    reporter = ReportGenerator(db)
    stats = reporter.get_feedback_summary_report(college_id)
    
    # Apply additional filters
    if event_id:
        stats = [s for s in stats if s["event_id"] == event_id]
    if event_type:
        stats = [s for s in stats if s["event_type"] == event_type]
    if start_date:
        stats = [s for s in stats if s["start_time"] >= start_date]
    if end_date:
        stats = [s for s in stats if s["start_time"] <= end_date]
    
    return {"feedback_stats": stats}


@app.get("/reports/top-students/")
async def get_top_students(
    college_id: Optional[int] = None,
    limit: int = 3,
    db: Session = Depends(get_db)
):
    """Get top N most active students"""
    reporter = ReportGenerator(db)
    top_students = reporter.get_top_active_students(college_id, limit)
    return {"top_students": top_students}


@app.get("/reports/events/")
async def get_event_stats(
    college_id: Optional[int] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get comprehensive event statistics with filters"""
    reporter = ReportGenerator(db)
    
    # Get event popularity report
    popularity = reporter.get_event_popularity_report(college_id)
    
    # Get event type breakdown
    type_breakdown = reporter.get_event_type_breakdown(college_id)
    
    # Apply filters
    if event_type:
        popularity = [e for e in popularity if e["event_type"] == event_type]
        type_breakdown = [t for t in type_breakdown if t["event_type"] == event_type]
    
    if status:
        # Filter by status (requires additional query)
        events = db.query(Event).filter(Event.status == status)
        if college_id:
            events = events.filter(Event.college_id == college_id)
        if start_date:
            events = events.filter(Event.start_time >= start_date)
        if end_date:
            events = events.filter(Event.end_time <= end_date)
        
        event_ids = [e.id for e in events.all()]
        popularity = [e for e in popularity if e["id"] in event_ids]
    
    if start_date:
        popularity = [e for e in popularity if e["start_time"] >= start_date]
    if end_date:
        popularity = [e for e in popularity if e["start_time"] <= end_date]
    
    return {
        "event_popularity": popularity,
        "event_type_breakdown": type_breakdown,
        "filters_applied": {
            "college_id": college_id,
            "event_type": event_type,
            "status": status,
            "start_date": start_date,
            "end_date": end_date
        }
    }


@app.get("/reports/comprehensive/")
async def get_comprehensive_report(
    college_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get comprehensive report with all statistics"""
    reporter = ReportGenerator(db)
    return generate_all_reports(db, college_id)


# ==================== BULK OPERATIONS ====================

@app.post("/bulk/students/")
async def bulk_create_students(
    college_id: int,
    students: List[StudentCreate],
    db: Session = Depends(get_db)
):
    """Bulk create students for a college"""
    # Check if college exists
    college = db.query(College).filter(College.id == college_id).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    created_students = []
    errors = []
    
    for i, student_data in enumerate(students):
        try:
            # Check for duplicate student_id
            existing = db.query(Student).filter(
                Student.college_id == college_id,
                Student.student_id == student_data.student_id
            ).first()
            
            if existing:
                errors.append(f"Row {i+1}: Student ID {student_data.student_id} already exists")
                continue
            
            student = Student(college_id=college_id, **student_data.dict())
            db.add(student)
            created_students.append(student)
            
        except Exception as e:
            errors.append(f"Row {i+1}: {str(e)}")
    
    if created_students:
        db.commit()
        for student in created_students:
            db.refresh(student)
    
    return {
        "created_count": len(created_students),
        "error_count": len(errors),
        "created_students": created_students,
        "errors": errors
    }


# ==================== SEARCH ENDPOINTS ====================

@app.get("/search/events/")
async def search_events(
    q: str = Query(..., description="Search term"),
    college_id: Optional[int] = None,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search events by title or description"""
    query = db.query(Event).filter(
        Event.title.contains(q) | Event.description.contains(q)
    )
    
    if college_id:
        query = query.filter(Event.college_id == college_id)
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    events = query.limit(20).all()
    return {"results": events, "query": q, "count": len(events)}


@app.get("/search/students/")
async def search_students(
    q: str = Query(..., description="Search term"),
    college_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Search students by name, email, or student_id"""
    query = db.query(Student).filter(
        Student.name.contains(q) |
        Student.email.contains(q) |
        Student.student_id.contains(q)
    )
    
    if college_id:
        query = query.filter(Student.college_id == college_id)
    
    students = query.limit(20).all()
    return {"results": students, "query": q, "count": len(students)}


# ==================== STATISTICS ENDPOINTS ====================

@app.get("/stats/overview/")
async def get_system_overview(db: Session = Depends(get_db)):
    """Get system-wide statistics overview"""
    reporter = ReportGenerator(db)
    return reporter.get_system_overview_report()


@app.get("/stats/college/{college_id}")
async def get_college_stats(college_id: int, db: Session = Depends(get_db)):
    """Get comprehensive statistics for a specific college"""
    reporter = ReportGenerator(db)
    return reporter.get_college_performance_report(college_id)


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
