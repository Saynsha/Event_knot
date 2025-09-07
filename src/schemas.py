"""
Pydantic schemas for request/response models in Campus Event Management Platform.
Defines data validation and serialization for API endpoints.
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime


# ==================== COLLEGE SCHEMAS ====================

class CollegeBase(BaseModel):
    name: str
    location: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class CollegeCreate(CollegeBase):
    pass


class CollegeUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class CollegeResponse(CollegeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== STUDENT SCHEMAS ====================

class StudentBase(BaseModel):
    college_id: int
    student_id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== EVENT SCHEMAS ====================

class EventBase(BaseModel):
    college_id: int
    title: str
    description: Optional[str] = None
    event_type: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    max_capacity: int = 100
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v
    
    @validator('max_capacity')
    def max_capacity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Max capacity must be positive')
        return v


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    max_capacity: Optional[int] = None
    status: Optional[str] = None
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v
    
    @validator('max_capacity')
    def max_capacity_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Max capacity must be positive')
        return v


class EventResponse(EventBase):
    id: int
    current_registrations: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== REGISTRATION SCHEMAS ====================

class RegistrationBase(BaseModel):
    student_id: int
    event_id: int


class RegistrationCreate(RegistrationBase):
    pass


class RegistrationResponse(RegistrationBase):
    id: int
    registered_at: datetime
    status: str
    
    class Config:
        from_attributes = True


# ==================== ATTENDANCE SCHEMAS ====================

class AttendanceBase(BaseModel):
    registration_id: int
    action: str  # "check_in" or "check_out"
    
    @validator('action')
    def action_must_be_valid(cls, v):
        if v not in ['check_in', 'check_out']:
            raise ValueError('Action must be either "check_in" or "check_out"')
        return v


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: int
    registration_id: int
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    status: str
    
    class Config:
        from_attributes = True


# ==================== FEEDBACK SCHEMAS ====================

class FeedbackBase(BaseModel):
    registration_id: int
    rating: int
    comment: Optional[str] = None
    
    @validator('rating')
    def rating_must_be_valid(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackResponse(FeedbackBase):
    id: int
    submitted_at: datetime
    
    class Config:
        from_attributes = True


# ==================== REPORT SCHEMAS ====================

class RegistrationStatsResponse(BaseModel):
    event_id: int
    event_title: str
    event_type: str
    start_time: datetime
    max_capacity: int
    current_registrations: int
    total_registrations: int
    registration_percentage: float


class AttendanceStatsResponse(BaseModel):
    event_id: int
    event_title: str
    event_type: str
    start_time: datetime
    total_registrations: int
    total_attendance: int
    present_count: int
    attendance_percentage: float


class FeedbackStatsResponse(BaseModel):
    event_id: int
    event_title: str
    event_type: str
    start_time: datetime
    total_feedback: int
    average_rating: float


class StudentStatsResponse(BaseModel):
    student_id: int
    student_name: str
    student_email: str
    college_name: str
    total_registrations: int
    total_attendance: int
    events_attended: int
    attendance_rate: float


class EventStatsResponse(BaseModel):
    event_id: int
    event_title: str
    event_type: str
    status: str
    start_time: datetime
    max_capacity: int
    current_registrations: int
    total_attendance: int
    present_count: int
    attendance_percentage: float
    registration_percentage: float
    average_rating: float


# ==================== BULK OPERATION SCHEMAS ====================

class BulkStudentCreate(BaseModel):
    college_id: int
    students: List[StudentCreate]


class BulkEventCreate(BaseModel):
    college_id: int
    events: List[EventCreate]


# ==================== SEARCH AND FILTER SCHEMAS ====================

class EventSearchParams(BaseModel):
    college_id: Optional[int] = None
    event_type: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_term: Optional[str] = None


class StudentSearchParams(BaseModel):
    college_id: Optional[int] = None
    search_term: Optional[str] = None


class ReportFilters(BaseModel):
    college_id: Optional[int] = None
    event_id: Optional[int] = None
    event_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

