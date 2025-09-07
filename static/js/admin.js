// Admin Dashboard JavaScript
const API_BASE_URL = '';

// Global state
let currentSection = 'dashboard';
let events = [];
let students = [];
let colleges = [];
let registrations = [];
let attendance = [];
let feedback = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    loadColleges();
    loadEvents();
    loadStudents();
    loadFeedback();
});

// Navigation functions
function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(el => {
        el.style.display = 'none';
    });
    
    // Remove active class from all nav links
    document.querySelectorAll('.nav-link').forEach(el => {
        el.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(section + '-section').style.display = 'block';
    
    // Add active class to selected nav link
    document.querySelector(`[onclick="showSection('${section}')"]`).classList.add('active');
    
    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'events': 'Event Management',
        'students': 'Student Management',
        'attendance': 'Attendance Tracking',
        'feedback': 'Feedback Management',
        'reports': 'Reports & Analytics',
        'colleges': 'College Management'
    };
    document.getElementById('page-title').textContent = titles[section];
    
    currentSection = section;
    
    // Load section-specific data
    switch(section) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'events':
            loadEvents();
            break;
        case 'students':
            loadStudents();
            break;
        case 'attendance':
            loadAttendanceData();
            break;
        case 'feedback':
            loadFeedback();
            break;
        case 'reports':
            loadReports();
            break;
        case 'colleges':
            loadColleges();
            break;
    }
}

// API Helper functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        if (!response.ok) {
            let detail = '';
            try {
                const err = await response.json();
                detail = err.detail ? (Array.isArray(err.detail) ? JSON.stringify(err.detail) : err.detail) : JSON.stringify(err);
            } catch (_) {
                detail = await response.text();
            }
            throw new Error(`HTTP ${response.status}: ${detail}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showAlert('Error: ' + error.message, 'danger');
        return null;
    }
}

// Dashboard functions
async function loadDashboardData() {
    try {
        // Load system overview
        const overview = await apiCall('/stats/overview/');
        if (overview) {
            document.getElementById('total-events').textContent = overview.system_overview.total_events || 0;
            document.getElementById('total-students').textContent = overview.system_overview.total_students || 0;
            document.getElementById('active-events').textContent = overview.system_overview.active_events || 0;
            document.getElementById('total-registrations').textContent = overview.system_overview.total_registrations || 0;
        }
        
        // Load recent events
        const recentEvents = await apiCall('/events/?limit=5');
        if (recentEvents) {
            displayRecentEvents(recentEvents);
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function displayRecentEvents(events) {
    const tbody = document.getElementById('recent-events-table');
    tbody.innerHTML = '';
    
    events.forEach(event => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${event.title}</td>
            <td><span class="badge bg-primary">${event.event_type}</span></td>
            <td>${new Date(event.start_time).toLocaleDateString()}</td>
            <td>${event.current_registrations}/${event.max_capacity}</td>
            <td><span class="badge bg-${event.status === 'active' ? 'success' : event.status === 'completed' ? 'info' : 'danger'}">${event.status}</span></td>
        `;
        tbody.appendChild(row);
    });
}

// Event management functions
async function loadEvents() {
    try {
        const eventsData = await apiCall('/events/');
        if (eventsData) {
            events = eventsData;
            displayEvents(events);
        }
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

function displayEvents(eventsList) {
    const tbody = document.getElementById('events-table');
    tbody.innerHTML = '';
    
    eventsList.forEach(event => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${event.id}</td>
            <td>${event.title}</td>
            <td><span class="badge bg-primary">${event.event_type}</span></td>
            <td>${new Date(event.start_time).toLocaleString()}</td>
            <td>${event.max_capacity}</td>
            <td>${event.current_registrations}</td>
            <td><span class="badge bg-${event.status === 'active' ? 'success' : event.status === 'completed' ? 'info' : 'danger'}">${event.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editEvent(${event.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteEvent(${event.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function showCreateEventModal() {
    const modal = `
        <div class="modal fade" id="createEventModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Create New Event</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="createEventForm">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Event Title *</label>
                                        <input type="text" class="form-control" id="eventTitle" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Event Type *</label>
                                        <select class="form-select" id="eventType" required>
                                            <option value="">Select Type</option>
                                            <option value="Conference">Conference</option>
                                            <option value="Workshop">Workshop</option>
                                            <option value="Sports">Sports</option>
                                            <option value="Cultural">Cultural</option>
                                            <option value="Academic">Academic</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea class="form-control" id="eventDescription" rows="3"></textarea>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Start Time *</label>
                                        <input type="datetime-local" class="form-control" id="eventStartTime" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">End Time *</label>
                                        <input type="datetime-local" class="form-control" id="eventEndTime" required>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Location</label>
                                        <input type="text" class="form-control" id="eventLocation">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Max Capacity *</label>
                                        <input type="number" class="form-control" id="eventCapacity" min="1" required>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">College *</label>
                                <select class="form-select" id="eventCollege" required>
                                    <option value="">Select College</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="createEvent()">Create Event</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('modals-container').innerHTML = modal;
    const modalElement = new bootstrap.Modal(document.getElementById('createEventModal'));
    modalElement.show();
    
    // Populate college dropdown
    populateCollegeDropdown('eventCollege');
}

async function createEvent() {
    const form = document.getElementById('createEventForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const collegeId = parseInt(document.getElementById('eventCollege').value);
    const start = document.getElementById('eventStartTime').value;
    const end = document.getElementById('eventEndTime').value;
    const capacity = parseInt(document.getElementById('eventCapacity').value);

    if (isNaN(collegeId)) { showAlert('Please select a college', 'warning'); return; }
    if (!start || !end) { showAlert('Please provide start and end time', 'warning'); return; }
    if (new Date(start) >= new Date(end)) { showAlert('End time must be after start time', 'warning'); return; }
    if (isNaN(capacity) || capacity <= 0) { showAlert('Capacity must be a positive number', 'warning'); return; }

    const eventData = {
        college_id: collegeId,
        title: document.getElementById('eventTitle').value,
        description: document.getElementById('eventDescription').value,
        event_type: document.getElementById('eventType').value,
        start_time: start + (start.length === 16 ? ':00' : ''),
        end_time: end + (end.length === 16 ? ':00' : ''),
        location: document.getElementById('eventLocation').value,
        max_capacity: capacity
    };
    
    const result = await apiCall('/events/', 'POST', eventData);
    if (result) {
        showAlert('Event created successfully!', 'success');
        bootstrap.Modal.getInstance(document.getElementById('createEventModal')).hide();
        loadEvents();
        loadDashboardData();
    }
}

// Student management functions
async function loadStudents() {
    try {
        const studentsData = await apiCall('/students/');
        if (studentsData) {
            students = studentsData;
            displayStudents(students);
        }
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

function displayStudents(studentsList) {
    const tbody = document.getElementById('students-table');
    tbody.innerHTML = '';
    
    studentsList.forEach(student => {
        const college = colleges.find(c => c.id === student.college_id);
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${student.id}</td>
            <td>${student.student_id}</td>
            <td>${student.name}</td>
            <td>${student.email}</td>
            <td>${college ? college.name : 'Unknown'}</td>
            <td>${student.phone || 'N/A'}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editStudent(${student.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteStudent(${student.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function showCreateStudentModal() {
    const modal = `
        <div class="modal fade" id="createStudentModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Student</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="createStudentForm">
                            <div class="mb-3">
                                <label class="form-label">College *</label>
                                <select class="form-select" id="studentCollege" required>
                                    <option value="">Select College</option>
                                </select>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Student ID *</label>
                                        <input type="text" class="form-control" id="studentId" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Full Name *</label>
                                        <input type="text" class="form-control" id="studentName" required>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Email *</label>
                                        <input type="email" class="form-control" id="studentEmail" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Phone</label>
                                        <input type="tel" class="form-control" id="studentPhone">
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="createStudent()">Add Student</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('modals-container').innerHTML = modal;
    const modalElement = new bootstrap.Modal(document.getElementById('createStudentModal'));
    modalElement.show();
    
    // Populate college dropdown
    populateCollegeDropdown('studentCollege');
}

async function createStudent() {
    const form = document.getElementById('createStudentForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const collegeId = parseInt(document.getElementById('studentCollege').value);
    if (isNaN(collegeId)) { showAlert('Please select a college', 'warning'); return; }

    const email = document.getElementById('studentEmail').value;
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { showAlert('Please enter a valid email address', 'warning'); return; }
    
    const studentData = {
        college_id: collegeId,
        student_id: document.getElementById('studentId').value,
        name: document.getElementById('studentName').value,
        email: email,
        phone: document.getElementById('studentPhone').value || null
    };
    
    const result = await apiCall('/students/', 'POST', studentData);
    if (result) {
        showAlert('Student added successfully!', 'success');
        bootstrap.Modal.getInstance(document.getElementById('createStudentModal')).hide();
        loadStudents();
        loadDashboardData();
    }
}

// College management functions
async function loadColleges() {
    try {
        const collegesData = await apiCall('/colleges/');
        if (collegesData) {
            colleges = collegesData;
            displayColleges(colleges);
            populateCollegeDropdowns();
        }
    } catch (error) {
        console.error('Error loading colleges:', error);
    }
}

function displayColleges(collegesList) {
    const tbody = document.getElementById('colleges-table');
    tbody.innerHTML = '';
    
    collegesList.forEach(college => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${college.id}</td>
            <td>${college.name}</td>
            <td>${college.location || 'N/A'}</td>
            <td>${college.contact_email || 'N/A'}</td>
            <td>${students.filter(s => s.college_id === college.id).length}</td>
            <td>${events.filter(e => e.college_id === college.id).length}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editCollege(${college.id})">
                    <i class="fas fa-edit"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function populateCollegeDropdowns() {
    const dropdowns = ['eventCollege', 'studentCollege', 'college-filter'];
    dropdowns.forEach(dropdownId => {
        const dropdown = document.getElementById(dropdownId);
        if (dropdown) {
            dropdown.innerHTML = '<option value="">Select College</option>';
            colleges.forEach(college => {
                const option = document.createElement('option');
                option.value = college.id;
                option.textContent = college.name;
                dropdown.appendChild(option);
            });
        }
    });
}

function populateCollegeDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    if (dropdown) {
        dropdown.innerHTML = '<option value="">Select College</option>';
        colleges.forEach(college => {
            const option = document.createElement('option');
            option.value = college.id;
            option.textContent = college.name;
            dropdown.appendChild(option);
        });
    }
}

// Attendance functions
async function loadAttendanceData() {
    try {
        const attendanceData = await apiCall('/attendance/');
        if (attendanceData) {
            attendance = attendanceData;
        }
        
        // Populate event dropdown
        const eventSelect = document.getElementById('attendance-event-select');
        eventSelect.innerHTML = '<option value="">Select Event</option>';
        events.forEach(event => {
            const option = document.createElement('option');
            option.value = event.id;
            option.textContent = `${event.title} - ${new Date(event.start_time).toLocaleDateString()}`;
            eventSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading attendance data:', error);
    }
}

async function loadEventAttendance() {
    const eventId = document.getElementById('attendance-event-select').value;
    if (!eventId) {
        showAlert('Please select an event first', 'warning');
        return;
    }
    
    try {
        const registrations = await apiCall(`/register/?event_id=${eventId}`);
        const attendanceData = await apiCall(`/attendance/?event_id=${eventId}`);
        
        displayAttendance(registrations, attendanceData);
    } catch (error) {
        console.error('Error loading event attendance:', error);
    }
}

function displayAttendance(registrations, attendanceRecords) {
    const tbody = document.getElementById('attendance-table');
    tbody.innerHTML = '';
    
    registrations.forEach(registration => {
        const student = students.find(s => s.id === registration.student_id);
        const attendance = attendanceRecords.find(a => a.registration_id === registration.id);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${student ? student.name : 'Unknown'}</td>
            <td>${student ? student.student_id : 'N/A'}</td>
            <td>${attendance && attendance.check_in_time ? new Date(attendance.check_in_time).toLocaleString() : 'Not checked in'}</td>
            <td>${attendance && attendance.check_out_time ? new Date(attendance.check_out_time).toLocaleString() : 'Not checked out'}</td>
            <td><span class="badge bg-${attendance && attendance.status === 'present' ? 'success' : attendance && attendance.status === 'late' ? 'warning' : 'danger'}">${attendance ? attendance.status : 'absent'}</span></td>
            <td>
                ${!attendance || !attendance.check_in_time ? 
                    `<button class="btn btn-sm btn-success" onclick="markAttendance(${registration.id}, 'check_in')">Check In</button>` : 
                    (!attendance.check_out_time ? 
                        `<button class="btn btn-sm btn-warning" onclick="markAttendance(${registration.id}, 'check_out')">Check Out</button>` : 
                        '<span class="text-muted">Completed</span>'
                    )
                }
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function markAttendance(registrationId, action) {
    try {
        const result = await apiCall('/attendance/', 'POST', {
            registration_id: registrationId,
            action: action
        });
        
        if (result) {
            showAlert(`${action === 'check_in' ? 'Check-in' : 'Check-out'} successful!`, 'success');
            loadEventAttendance();
        }
    } catch (error) {
        console.error('Error marking attendance:', error);
    }
}

// Feedback functions
async function loadFeedback() {
    try {
        const feedbackData = await apiCall('/feedback/');
        if (feedbackData) {
            feedback = feedbackData;
            displayFeedback(feedback);
        }
    } catch (error) {
        console.error('Error loading feedback:', error);
    }
}

function displayFeedback(feedbackList) {
    const tbody = document.getElementById('feedback-table');
    tbody.innerHTML = '';
    
    feedbackList.forEach(feedbackItem => {
        const registration = registrations.find(r => r.id === feedbackItem.registration_id);
        const event = events.find(e => e.id === registration?.event_id);
        const student = students.find(s => s.id === registration?.student_id);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${event ? event.title : 'Unknown Event'}</td>
            <td>${student ? student.name : 'Unknown Student'}</td>
            <td>
                <div class="d-flex">
                    ${Array.from({length: 5}, (_, i) => 
                        `<i class="fas fa-star ${i < feedbackItem.rating ? 'text-warning' : 'text-muted'}"></i>`
                    ).join('')}
                </div>
            </td>
            <td>${feedbackItem.comment || 'No comment'}</td>
            <td>${new Date(feedbackItem.submitted_at).toLocaleString()}</td>
        `;
        tbody.appendChild(row);
    });
}

// Reports functions
async function loadReports() {
    try {
        const [popularity, topStudents] = await Promise.all([
            apiCall('/reports/events/'),
            apiCall('/reports/top-students/')
        ]);
        
        if (popularity) {
            displayEventPopularity(popularity.event_popularity || []);
        }
        
        if (topStudents) {
            displayTopStudents(topStudents.top_students || []);
        }
    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

function displayEventPopularity(popularityData) {
    const tbody = document.getElementById('popularity-table');
    tbody.innerHTML = '';
    
    popularityData.forEach(event => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${event.title}</td>
            <td>${event.total_registrations || 0}</td>
            <td>${event.max_capacity || 0}</td>
            <td>${event.registration_percentage || 0}%</td>
        `;
        tbody.appendChild(row);
    });
}

function displayTopStudents(studentsData) {
    const tbody = document.getElementById('top-students-table');
    tbody.innerHTML = '';
    
    studentsData.forEach(student => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${student.student_name}</td>
            <td>${student.events_attended || 0}</td>
            <td>${student.attendance_rate || 0}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

function refreshData() {
    showAlert('Refreshing data...', 'info');
    loadDashboardData();
    loadEvents();
    loadStudents();
    loadColleges();
    loadFeedback();
}

// Filter functions
function filterEvents() {
    const searchTerm = document.getElementById('event-search').value.toLowerCase();
    const typeFilter = document.getElementById('event-type-filter').value;
    const statusFilter = document.getElementById('event-status-filter').value;
    
    let filteredEvents = events;
    
    if (searchTerm) {
        filteredEvents = filteredEvents.filter(event => 
            event.title.toLowerCase().includes(searchTerm) ||
            event.description?.toLowerCase().includes(searchTerm)
        );
    }
    
    if (typeFilter) {
        filteredEvents = filteredEvents.filter(event => event.event_type === typeFilter);
    }
    
    if (statusFilter) {
        filteredEvents = filteredEvents.filter(event => event.status === statusFilter);
    }
    
    displayEvents(filteredEvents);
}

function filterStudents() {
    const searchTerm = document.getElementById('student-search').value.toLowerCase();
    const collegeFilter = document.getElementById('college-filter').value;
    
    let filteredStudents = students;
    
    if (searchTerm) {
        filteredStudents = filteredStudents.filter(student => 
            student.name.toLowerCase().includes(searchTerm) ||
            student.email.toLowerCase().includes(searchTerm) ||
            student.student_id.toLowerCase().includes(searchTerm)
        );
    }
    
    if (collegeFilter) {
        filteredStudents = filteredStudents.filter(student => student.college_id === parseInt(collegeFilter));
    }
    
    displayStudents(filteredStudents);
}

// Placeholder functions for edit/delete operations
function editEvent(eventId) {
    // Fetch event details then open edit modal
    apiCall(`/events/${eventId}`)
        .then(event => {
            if (!event) return;

            const startVal = formatDateTimeLocal(event.start_time);
            const endVal = formatDateTimeLocal(event.end_time);

            const modal = `
                <div class="modal fade" id="editEventModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Edit Event</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="editEventForm">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label class="form-label">Event Title *</label>
                                                <input type="text" class="form-control" id="editEventTitle" value="${event.title}" required>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label class="form-label">Event Type *</label>
                                                <select class="form-select" id="editEventType" required>
                                                    <option ${event.event_type==='Conference'?'selected':''} value="Conference">Conference</option>
                                                    <option ${event.event_type==='Workshop'?'selected':''} value="Workshop">Workshop</option>
                                                    <option ${event.event_type==='Sports'?'selected':''} value="Sports">Sports</option>
                                                    <option ${event.event_type==='Cultural'?'selected':''} value="Cultural">Cultural</option>
                                                    <option ${event.event_type==='Academic'?'selected':''} value="Academic">Academic</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Description</label>
                                        <textarea class="form-control" id="editEventDescription" rows="3">${event.description??''}</textarea>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label class="form-label">Start Time *</label>
                                                <input type="datetime-local" class="form-control" id="editEventStartTime" value="${startVal}" required>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label class="form-label">End Time *</label>
                                                <input type="datetime-local" class="form-control" id="editEventEndTime" value="${endVal}" required>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label class="form-label">Location</label>
                                                <input type="text" class="form-control" id="editEventLocation" value="${event.location??''}">
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="mb-3">
                                                <label class="form-label">Max Capacity *</label>
                                                <input type="number" class="form-control" id="editEventCapacity" value="${event.max_capacity}" min="1" required>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="mb-3">
                                                <label class="form-label">Status</label>
                                                <select class="form-select" id="editEventStatus">
                                                    <option ${event.status==='active'?'selected':''} value="active">Active</option>
                                                    <option ${event.status==='completed'?'selected':''} value="completed">Completed</option>
                                                    <option ${event.status==='cancelled'?'selected':''} value="cancelled">Cancelled</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <button type="button" class="btn btn-primary" onclick="submitEventUpdate(${event.id})">Save Changes</button>
                            </div>
                        </div>
                    </div>
                </div>`;

            document.getElementById('modals-container').innerHTML = modal;
            new bootstrap.Modal(document.getElementById('editEventModal')).show();
        });
}

function submitEventUpdate(eventId) {
    const form = document.getElementById('editEventForm');
    if (!form.checkValidity()) { form.reportValidity(); return; }

    const payload = {
        title: document.getElementById('editEventTitle').value,
        description: document.getElementById('editEventDescription').value,
        event_type: document.getElementById('editEventType').value,
        start_time: document.getElementById('editEventStartTime').value + ':00',
        end_time: document.getElementById('editEventEndTime').value + ':00',
        location: document.getElementById('editEventLocation').value,
        max_capacity: parseInt(document.getElementById('editEventCapacity').value),
        status: document.getElementById('editEventStatus').value
    };

    apiCall(`/events/${eventId}`, 'PUT', payload).then(result => {
        if (result) {
            showAlert('Event updated successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editEventModal')).hide();
            loadEvents();
            loadDashboardData();
        }
    });
}

function deleteEvent(eventId) {
    if (!confirm('Are you sure you want to cancel this event?')) { return; }
    apiCall(`/events/${eventId}`, 'DELETE').then(result => {
        if (result) {
            showAlert('Event cancelled successfully!', 'success');
            loadEvents();
            loadDashboardData();
        }
    });
}

function editCollege(collegeId) {
    apiCall(`/colleges/${collegeId}`).then(college => {
        if (!college) return;
        const modal = `
            <div class="modal fade" id="editCollegeModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Edit College</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="editCollegeForm">
                                <div class="mb-3">
                                    <label class="form-label">Name</label>
                                    <input class="form-control" id="collegeName" value="${college.name}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Location</label>
                                    <input class="form-control" id="collegeLocation" value="${college.location??''}">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Contact Email</label>
                                    <input class="form-control" id="collegeEmail" value="${college.contact_email??''}">
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary" onclick="submitCollegeUpdate(${college.id})">Save</button>
                        </div>
                    </div>
                </div>
            </div>`;
        document.getElementById('modals-container').innerHTML = modal;
        new bootstrap.Modal(document.getElementById('editCollegeModal')).show();
    });
}

function submitCollegeUpdate(collegeId) {
    const payload = {
        name: document.getElementById('collegeName').value,
        location: document.getElementById('collegeLocation').value,
        contact_email: document.getElementById('collegeEmail').value
    };
    apiCall(`/colleges/${collegeId}`, 'PUT', payload).then(result => {
        if (result) {
            showAlert('College updated!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editCollegeModal')).hide();
            loadColleges();
        }
    });
}

function showCreateCollegeModal() {
    const modal = `
        <div class="modal fade" id="createCollegeModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add College</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="createCollegeForm">
                            <div class="mb-3">
                                <label class="form-label">Name *</label>
                                <input class="form-control" id="newCollegeName" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Location</label>
                                <input class="form-control" id="newCollegeLocation">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Contact Email</label>
                                <input class="form-control" id="newCollegeEmail" type="email">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="createCollege()">Create</button>
                    </div>
                </div>
            </div>
        </div>`;
    document.getElementById('modals-container').innerHTML = modal;
    new bootstrap.Modal(document.getElementById('createCollegeModal')).show();
}

function createCollege() {
    const form = document.getElementById('createCollegeForm');
    if (!form.checkValidity()) { form.reportValidity(); return; }

    const payload = {
        name: document.getElementById('newCollegeName').value,
        location: document.getElementById('newCollegeLocation').value,
        contact_email: document.getElementById('newCollegeEmail').value
    };

    apiCall('/colleges/', 'POST', payload).then(result => {
        if (result) {
            showAlert('College created successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createCollegeModal')).hide();
            loadColleges();
        }
    });
}

function formatDateTimeLocal(isoString) {
    if (!isoString) return '';
    const d = new Date(isoString);
    const pad = n => String(n).padStart(2, '0');
    const yyyy = d.getFullYear();
    const mm = pad(d.getMonth()+1);
    const dd = pad(d.getDate());
    const hh = pad(d.getHours());
    const mi = pad(d.getMinutes());
    return `${yyyy}-${mm}-${dd}T${hh}:${mi}`;
}

function showCreateModal() {
    showCreateEventModal();
}