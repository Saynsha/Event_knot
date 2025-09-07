"""
SQLAlchemy ORM models for Campus Event Management Platform.
Defines all database tables and their relationships.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class College(Base):
    """College/Institution model"""
    __tablename__ = "colleges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255))
    contact_email = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    students = relationship("Student", back_populates="college", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="college", cascade="all, delete-orphan")


class Student(Base):
    """Student model"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(String(50), nullable=False)  # Student ID within college
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    college = relationship("College", back_populates="students")
    registrations = relationship("Registration", back_populates="student", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("email LIKE '%@%'", name="check_email_format"),
        {"sqlite_autoincrement": True}
    )


class Event(Base):
    """Event model"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    event_type = Column(String(100), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(255))
    max_capacity = Column(Integer, default=100)
    current_registrations = Column(Integer, default=0)
    status = Column(String(20), default="active", index=True)  # active, cancelled, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    college = relationship("College", back_populates="events")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("max_capacity > 0", name="check_positive_capacity"),
        CheckConstraint("current_registrations >= 0", name="check_non_negative_registrations"),
        CheckConstraint("current_registrations <= max_capacity", name="check_capacity_limit"),
        CheckConstraint("end_time > start_time", name="check_end_after_start"),
        CheckConstraint("status IN ('active', 'cancelled', 'completed')", name="check_valid_status"),
        {"sqlite_autoincrement": True}
    )


class Registration(Base):
    """Student event registration model"""
    __tablename__ = "registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    status = Column(String(20), default="registered", index=True)  # registered, cancelled, attended
    
    # Relationships
    student = relationship("Student", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
    attendance = relationship("Attendance", back_populates="registration", cascade="all, delete-orphan", uselist=False)
    feedback = relationship("Feedback", back_populates="registration", cascade="all, delete-orphan", uselist=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('registered', 'cancelled', 'attended')", name="check_valid_registration_status"),
        {"sqlite_autoincrement": True}
    )


class Attendance(Base):
    """Event attendance tracking model"""
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False, unique=True)
    check_in_time = Column(DateTime(timezone=True), index=True)
    check_out_time = Column(DateTime(timezone=True))
    status = Column(String(20), default="absent", index=True)  # absent, present, late
    
    # Relationships
    registration = relationship("Registration", back_populates="attendance")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('absent', 'present', 'late')", name="check_valid_attendance_status"),
        CheckConstraint("check_out_time IS NULL OR check_out_time >= check_in_time", name="check_checkout_after_checkin"),
        {"sqlite_autoincrement": True}
    )


class Feedback(Base):
    """Event feedback model"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False, unique=True)
    rating = Column(Integer, nullable=False, index=True)
    comment = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    registration = relationship("Registration", back_populates="feedback")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
        {"sqlite_autoincrement": True}
    )


# Create indexes for better query performance
def create_indexes(engine):
    """Create additional indexes for better query performance"""
    from sqlalchemy import Index
    
    # Composite indexes for common queries
    Index('idx_student_college', Student.college_id, Student.student_id)
    Index('idx_event_college_type', Event.college_id, Event.event_type)
    Index('idx_event_status_time', Event.status, Event.start_time)
    Index('idx_registration_student_event', Registration.student_id, Registration.event_id)
    Index('idx_attendance_status', Attendance.status)
    Index('idx_feedback_rating', Feedback.rating)

