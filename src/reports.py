"""
Reporting module for Campus Event Management Platform.
Contains direct SQL queries and reporting functions for analytics and insights.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_, desc, asc
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json

from .models import College, Student, Event, Registration, Attendance, Feedback


class ReportGenerator:
    """Main class for generating various reports using SQL queries"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== EVENT POPULARITY REPORTS ====================
    
    def get_event_popularity_report(self, college_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """
        Get events sorted by registration count (most popular first)
        """
        query = text("""
            SELECT 
                e.id,
                e.title,
                e.event_type,
                e.start_time,
                e.max_capacity,
                e.current_registrations,
                COUNT(r.id) as total_registrations,
                ROUND((e.current_registrations * 100.0 / e.max_capacity), 2) as registration_percentage
            FROM events e
            LEFT JOIN registrations r ON e.id = r.event_id
            WHERE e.status = 'active'
            {college_filter}
            GROUP BY e.id, e.title, e.event_type, e.start_time, e.max_capacity, e.current_registrations
            ORDER BY total_registrations DESC, e.current_registrations DESC
            LIMIT :limit
        """)
        
        params = {"limit": limit}
        if college_id:
            query = text(query.text.replace("{college_filter}", "AND e.college_id = :college_id"))
            params["college_id"] = college_id
        else:
            query = text(query.text.replace("{college_filter}", ""))
        
        result = self.db.execute(query, params)
        return [dict(row._mapping) for row in result]
    
    def get_event_type_breakdown(self, college_id: Optional[int] = None) -> List[Dict]:
        """
        Get breakdown of events by type with statistics
        """
        query = text("""
            SELECT 
                e.event_type,
                COUNT(e.id) as total_events,
                SUM(e.current_registrations) as total_registrations,
                AVG(e.current_registrations) as avg_registrations,
                ROUND(AVG(e.current_registrations * 100.0 / e.max_capacity), 2) as avg_registration_percentage
            FROM events e
            WHERE e.status = 'active'
            {college_filter}
            GROUP BY e.event_type
            ORDER BY total_registrations DESC
        """)
        
        params = {}
        if college_id:
            query = text(query.text.replace("{college_filter}", "AND e.college_id = :college_id"))
            params["college_id"] = college_id
        else:
            query = text(query.text.replace("{college_filter}", ""))
        
        result = self.db.execute(query, params)
        return [dict(row._mapping) for row in result]
    
    # ==================== STUDENT PARTICIPATION REPORTS ====================
    
    def get_student_participation_report(self, college_id: Optional[int] = None, limit: int = 20) -> List[Dict]:
        """
        Get students sorted by number of events attended
        """
        query = text("""
            SELECT 
                s.id,
                s.name,
                s.email,
                c.name as college_name,
                COUNT(DISTINCT r.event_id) as total_registrations,
                COUNT(DISTINCT a.registration_id) as total_attendance,
                SUM(CASE WHEN a.status IN ('present', 'late') THEN 1 ELSE 0 END) as events_attended,
                ROUND(
                    (SUM(CASE WHEN a.status IN ('present', 'late') THEN 1 ELSE 0 END) * 100.0 / 
                     COUNT(DISTINCT r.event_id)), 2
                ) as attendance_rate
            FROM students s
            JOIN colleges c ON s.college_id = c.id
            LEFT JOIN registrations r ON s.id = r.student_id
            LEFT JOIN attendance a ON r.id = a.registration_id
            {college_filter}
            GROUP BY s.id, s.name, s.email, c.name
            HAVING total_registrations > 0
            ORDER BY events_attended DESC, attendance_rate DESC
            LIMIT :limit
        """)
        
        params = {"limit": limit}
        if college_id:
            query = text(query.text.replace("{college_filter}", "WHERE s.college_id = :college_id"))
            params["college_id"] = college_id
        else:
            query = text(query.text.replace("{college_filter}", ""))
        
        result = self.db.execute(query, params)
        return [dict(row._mapping) for row in result]
    
    def get_top_active_students(self, college_id: Optional[int] = None, limit: int = 3) -> List[Dict]:
        """
        Get top N most active students across all events
        """
        return self.get_student_participation_report(college_id, limit)
    
    def get_student_engagement_by_college(self) -> List[Dict]:
        """
        Get student engagement statistics by college
        """
        query = text("""
            SELECT 
                c.id as college_id,
                c.name as college_name,
                COUNT(DISTINCT s.id) as total_students,
                COUNT(DISTINCT r.event_id) as total_registrations,
                COUNT(DISTINCT a.registration_id) as total_attendance,
                ROUND(
                    (COUNT(DISTINCT a.registration_id) * 100.0 / COUNT(DISTINCT r.event_id)), 2
                ) as overall_attendance_rate,
                ROUND(AVG(f.rating), 2) as avg_feedback_rating
            FROM colleges c
            LEFT JOIN students s ON c.id = s.college_id
            LEFT JOIN registrations r ON s.id = r.student_id
            LEFT JOIN attendance a ON r.id = a.registration_id
            LEFT JOIN feedback f ON r.id = f.registration_id
            GROUP BY c.id, c.name
            ORDER BY overall_attendance_rate DESC
        """)
        
        result = self.db.execute(query)
        return [dict(row._mapping) for row in result]
    
    # ==================== ATTENDANCE REPORTS ====================
    
    def get_attendance_summary_report(self, college_id: Optional[int] = None) -> List[Dict]:
        """
        Get comprehensive attendance summary for all events
        """
        query = text("""
            SELECT 
                e.id as event_id,
                e.title,
                e.event_type,
                e.start_time,
                e.max_capacity,
                e.current_registrations,
                COUNT(a.id) as total_attendance_records,
                SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN a.status = 'late' THEN 1 ELSE 0 END) as late_count,
                SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) as absent_count,
                ROUND(
                    ((SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) + 
                      SUM(CASE WHEN a.status = 'late' THEN 1 ELSE 0 END)) * 100.0 / 
                     e.current_registrations), 2
                ) as attendance_percentage
            FROM events e
            LEFT JOIN registrations r ON e.id = r.event_id
            LEFT JOIN attendance a ON r.id = a.registration_id
            WHERE e.status IN ('active', 'completed')
            {college_filter}
            GROUP BY e.id, e.title, e.event_type, e.start_time, e.max_capacity, e.current_registrations
            ORDER BY attendance_percentage DESC
        """)
        
        params = {}
        if college_id:
            query = text(query.text.replace("{college_filter}", "AND e.college_id = :college_id"))
            params["college_id"] = college_id
        else:
            query = text(query.text.replace("{college_filter}", ""))
        
        result = self.db.execute(query, params)
        return [dict(row._mapping) for row in result]
    
    def get_attendance_trends(self, days: int = 30, college_id: Optional[int] = None) -> List[Dict]:
        """
        Get attendance trends over the last N days
        """
        query = text("""
            SELECT 
                DATE(e.start_time) as event_date,
                COUNT(DISTINCT e.id) as total_events,
                SUM(e.current_registrations) as total_registrations,
                SUM(a.present_count) as total_present,
                SUM(a.late_count) as total_late,
                ROUND(
                    ((SUM(a.present_count) + SUM(a.late_count)) * 100.0 / 
                     SUM(e.current_registrations)), 2
                ) as daily_attendance_rate
            FROM events e
            LEFT JOIN (
                SELECT 
                    r.event_id,
                    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present_count,
                    SUM(CASE WHEN a.status = 'late' THEN 1 ELSE 0 END) as late_count
                FROM registrations r
                LEFT JOIN attendance a ON r.id = a.registration_id
                GROUP BY r.event_id
            ) a ON e.id = a.event_id
            WHERE e.start_time >= :start_date
            {college_filter}
            GROUP BY DATE(e.start_time)
            ORDER BY event_date DESC
        """)
        
        start_date = datetime.now() - timedelta(days=days)
        params = {"start_date": start_date}
        
        if college_id:
            query = text(query.text.replace("{college_filter}", "AND e.college_id = :college_id"))
            params["college_id"] = college_id
        else:
            query = text(query.text.replace("{college_filter}", ""))
        
        result = self.db.execute(query, params)
        return [dict(row._mapping) for row in result]
    
    # ==================== FEEDBACK REPORTS ====================
    
    def get_feedback_summary_report(self, college_id: Optional[int] = None) -> List[Dict]:
        """
        Get comprehensive feedback summary for all events
        """
        query = text("""
            SELECT 
                e.id as event_id,
                e.title,
                e.event_type,
                e.start_time,
                COUNT(f.id) as total_feedback,
                ROUND(AVG(f.rating), 2) as average_rating,
                SUM(CASE WHEN f.rating = 5 THEN 1 ELSE 0 END) as excellent_count,
                SUM(CASE WHEN f.rating = 4 THEN 1 ELSE 0 END) as good_count,
                SUM(CASE WHEN f.rating = 3 THEN 1 ELSE 0 END) as average_count,
                SUM(CASE WHEN f.rating = 2 THEN 1 ELSE 0 END) as poor_count,
                SUM(CASE WHEN f.rating = 1 THEN 1 ELSE 0 END) as terrible_count
            FROM events e
            LEFT JOIN registrations r ON e.id = r.event_id
            LEFT JOIN feedback f ON r.id = f.registration_id
            WHERE e.status IN ('active', 'completed')
            {college_filter}
            GROUP BY e.id, e.title, e.event_type, e.start_time
            HAVING total_feedback > 0
            ORDER BY average_rating DESC
        """)
        
        params = {}
        if college_id:
            query = text(query.text.replace("{college_filter}", "AND e.college_id = :college_id"))
            params["college_id"] = college_id
        else:
            query = text(query.text.replace("{college_filter}", ""))
        
        result = self.db.execute(query, params)
        return [dict(row._mapping) for row in result]
    
    def get_feedback_distribution(self, college_id: Optional[int] = None) -> Dict:
        """
        Get overall feedback rating distribution
        """
        query = text("""
            SELECT 
                f.rating,
                COUNT(f.id) as count,
                ROUND((COUNT(f.id) * 100.0 / (SELECT COUNT(*) FROM feedback)), 2) as percentage
            FROM feedback f
            JOIN registrations r ON f.registration_id = r.id
            JOIN events e ON r.event_id = e.id
            {college_filter}
            GROUP BY f.rating
            ORDER BY f.rating DESC
        """)
        
        params = {}
        if college_id:
            query = text(query.text.replace("{college_filter}", "WHERE e.college_id = :college_id"))
            params["college_id"] = college_id
        else:
            query = text(query.text.replace("{college_filter}", ""))
        
        result = self.db.execute(query, params)
        distribution = {}
        for row in result:
            distribution[f"rating_{row.rating}"] = {
                "count": row.count,
                "percentage": row.percentage
            }
        
        return distribution
    
    # ==================== COMPREHENSIVE REPORTS ====================
    
    def get_college_performance_report(self, college_id: int) -> Dict:
        """
        Get comprehensive performance report for a specific college
        """
        # Basic college info
        college = self.db.query(College).filter(College.id == college_id).first()
        if not college:
            return {"error": "College not found"}
        
        # Student count
        student_count = self.db.query(Student).filter(Student.college_id == college_id).count()
        
        # Event statistics
        event_stats = self.db.query(
            func.count(Event.id).label('total_events'),
            func.sum(Event.current_registrations).label('total_registrations'),
            func.avg(Event.current_registrations).label('avg_registrations')
        ).filter(Event.college_id == college_id).first()
        
        # Attendance statistics
        attendance_stats = self.db.query(
            func.count(Attendance.id).label('total_attendance'),
            func.sum(func.case([(Attendance.status == 'present', 1)], else_=0)).label('present_count'),
            func.sum(func.case([(Attendance.status == 'late', 1)], else_=0)).label('late_count')
        ).join(Registration).join(Event).filter(Event.college_id == college_id).first()
        
        # Feedback statistics
        feedback_stats = self.db.query(
            func.count(Feedback.id).label('total_feedback'),
            func.avg(Feedback.rating).label('avg_rating')
        ).join(Registration).join(Event).filter(Event.college_id == college_id).first()
        
        return {
            "college": {
                "id": college.id,
                "name": college.name,
                "location": college.location,
                "contact_email": college.contact_email
            },
            "statistics": {
                "total_students": student_count,
                "total_events": event_stats.total_events or 0,
                "total_registrations": event_stats.total_registrations or 0,
                "average_registrations_per_event": round(event_stats.avg_registrations or 0, 2),
                "total_attendance_records": attendance_stats.total_attendance or 0,
                "present_count": attendance_stats.present_count or 0,
                "late_count": attendance_stats.late_count or 0,
                "attendance_rate": round(
                    ((attendance_stats.present_count or 0) + (attendance_stats.late_count or 0)) * 100.0 / 
                    (event_stats.total_registrations or 1), 2
                ),
                "total_feedback": feedback_stats.total_feedback or 0,
                "average_rating": round(feedback_stats.avg_rating or 0, 2)
            }
        }
    
    def get_system_overview_report(self) -> Dict:
        """
        Get system-wide overview report
        """
        # College count
        college_count = self.db.query(College).count()
        
        # Student count
        student_count = self.db.query(Student).count()
        
        # Event statistics
        event_stats = self.db.query(
            func.count(Event.id).label('total_events'),
            func.sum(Event.current_registrations).label('total_registrations'),
            func.avg(Event.current_registrations).label('avg_registrations')
        ).first()
        
        # Active events
        active_events = self.db.query(Event).filter(Event.status == 'active').count()
        
        # Recent events (last 30 days)
        recent_events = self.db.query(Event).filter(
            Event.start_time >= datetime.now() - timedelta(days=30)
        ).count()
        
        return {
            "system_overview": {
                "total_colleges": college_count,
                "total_students": student_count,
                "total_events": event_stats.total_events or 0,
                "active_events": active_events,
                "recent_events_30_days": recent_events,
                "total_registrations": event_stats.total_registrations or 0,
                "average_registrations_per_event": round(event_stats.avg_registrations or 0, 2)
            }
        }
    
    # ==================== EXPORT FUNCTIONS ====================
    
    def export_report_to_json(self, report_data: List[Dict], filename: str) -> str:
        """
        Export report data to JSON file
        """
        filepath = f"reports/{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        return filepath
    
    def export_report_to_csv(self, report_data: List[Dict], filename: str) -> str:
        """
        Export report data to CSV file
        """
        import csv
        
        if not report_data:
            return None
        
        filepath = f"reports/{filename}.csv"
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=report_data[0].keys())
            writer.writeheader()
            writer.writerows(report_data)
        return filepath


# ==================== CONVENIENCE FUNCTIONS ====================

def generate_all_reports(db: Session, college_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Generate all available reports for easy access
    """
    reporter = ReportGenerator(db)
    
    return {
        "event_popularity": reporter.get_event_popularity_report(college_id),
        "event_type_breakdown": reporter.get_event_type_breakdown(college_id),
        "student_participation": reporter.get_student_participation_report(college_id),
        "top_active_students": reporter.get_top_active_students(college_id),
        "attendance_summary": reporter.get_attendance_summary_report(college_id),
        "attendance_trends": reporter.get_attendance_trends(college_id=college_id),
        "feedback_summary": reporter.get_feedback_summary_report(college_id),
        "feedback_distribution": reporter.get_feedback_distribution(college_id),
        "college_performance": reporter.get_college_performance_report(college_id) if college_id else None,
        "system_overview": reporter.get_system_overview_report()
    }

