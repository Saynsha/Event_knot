// Student App JavaScript
const API_BASE_URL = '';

// Global state
let currentSection = 'home';
let currentStudent = null;
let events = [];
let myRegistrations = [];
let myFeedback = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // For demo purposes, we'll use a mock student
    // In a real app, this would come from authentication
    currentStudent = {
        id: 1,
        name: 'John Doe',
        student_id: 'STU001',
        email: 'john.doe@university.edu',
        college_id: 1
    };
    
    document.getElementById('student-name').textContent = currentStudent.name;
    
    loadHomeData();
    loadEvents();
    loadMyEvents();
    loadMyFeedback();
    
    // Initialize rating stars
    initializeRatingStars();
});

// Navigation functions
function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(el => {
        el.style.display = 'none';
    });
    
    // Remove active class from all nav links
    document.querySelectorAll('.nav-pills .nav-link').forEach(el => {
        el.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(section + '-section').style.display = 'block';
    
    // Add active class to selected nav link
    document.querySelector(`[onclick="showSection('${section}')"]`).classList.add('active');
    
    currentSection = section;
    
    // Load section-specific data
    switch(section) {
        case 'home':
            loadHomeData();
            break;
        case 'events':
            loadEvents();
            break;
        case 'my-events':
            loadMyEvents();
            break;
        case 'feedback':
            loadMyFeedback();
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
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showAlert('Error: ' + error.message, 'danger');
        return null;
    }
}

// Home section functions
async function loadHomeData() {
    try {
        // Load upcoming events
        const upcomingEvents = await apiCall('/events/?status=active&limit=3');
        if (upcomingEvents) {
            displayRecentEvents(upcomingEvents);
            document.getElementById('upcoming-events-count').textContent = upcomingEvents.length;
        }
        
        // Load my registrations count
        const registrations = await apiCall(`/register/?student_id=${currentStudent.id}`);
        if (registrations) {
            myRegistrations = registrations;
            document.getElementById('registered-events-count').textContent = registrations.length;
        }
        
        // Load attendance count
        const attendance = await apiCall(`/attendance/?student_id=${currentStudent.id}`);
        if (attendance) {
            const attendedCount = attendance.filter(a => a.status === 'present' || a.status === 'late').length;
            document.getElementById('attended-events-count').textContent = attendedCount;
        }
        
        // Load feedback count
        const feedback = await apiCall(`/feedback/?student_id=${currentStudent.id}`);
        if (feedback) {
            myFeedback = feedback;
            document.getElementById('feedback-given-count').textContent = feedback.length;
        }
    } catch (error) {
        console.error('Error loading home data:', error);
    }
}

function displayRecentEvents(eventsList) {
    const container = document.getElementById('recent-events-list');
    container.innerHTML = '';
    
    if (eventsList.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No recent events available</p>';
        return;
    }
    
    eventsList.forEach(event => {
        const eventCard = createEventCard(event, true);
        container.appendChild(eventCard);
    });
}

// Events section functions
async function loadEvents() {
    try {
        const eventsData = await apiCall('/events/?status=active');
        if (eventsData) {
            events = eventsData;
            displayEvents(events);
        }
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

function displayEvents(eventsList) {
    const container = document.getElementById('events-list');
    container.innerHTML = '';
    
    if (eventsList.length === 0) {
        container.innerHTML = '<div class="text-center py-5"><p class="text-muted">No events available</p></div>';
        return;
    }
    
    eventsList.forEach(event => {
        const eventCard = createEventCard(event, false);
        container.appendChild(eventCard);
    });
}

function createEventCard(event, isCompact = false) {
    const card = document.createElement('div');
    card.className = `event-card card ${isCompact ? 'mb-3' : 'mb-4'}`;
    
    const registrationPercentage = (event.current_registrations / event.max_capacity) * 100;
    const isRegistered = myRegistrations.some(r => r.event_id === event.id);
    const canRegister = event.status === 'active' && event.current_registrations < event.max_capacity && !isRegistered;
    
    card.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <h6 class="card-title mb-0">${event.title}</h6>
                <span class="event-type-badge">${event.event_type}</span>
            </div>
            
            ${event.description ? `<p class="card-text text-muted small">${event.description.substring(0, 100)}${event.description.length > 100 ? '...' : ''}</p>` : ''}
            
            <div class="row mb-2">
                <div class="col-6">
                    <small class="text-muted">
                        <i class="fas fa-calendar me-1"></i>
                        ${new Date(event.start_time).toLocaleDateString()}
                    </small>
                </div>
                <div class="col-6">
                    <small class="text-muted">
                        <i class="fas fa-clock me-1"></i>
                        ${new Date(event.start_time).toLocaleTimeString()}
                    </small>
                </div>
            </div>
            
            ${event.location ? `
                <div class="mb-2">
                    <small class="text-muted">
                        <i class="fas fa-map-marker-alt me-1"></i>
                        ${event.location}
                    </small>
                </div>
            ` : ''}
            
            <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <small class="text-muted">Capacity</small>
                    <small class="text-muted">${event.current_registrations}/${event.max_capacity}</small>
                </div>
                <div class="capacity-bar">
                    <div class="capacity-fill" style="width: ${registrationPercentage}%"></div>
                </div>
            </div>
            
            <div class="d-flex justify-content-between align-items-center">
                <span class="badge bg-${event.status === 'active' ? 'success' : 'secondary'}">${event.status}</span>
                <div>
                    ${isRegistered ? 
                        '<span class="badge bg-info">Registered</span>' :
                        canRegister ?
                            `<button class="btn btn-primary btn-sm" onclick="registerForEvent(${event.id})">
                                <i class="fas fa-plus me-1"></i> Register
                            </button>` :
                            '<span class="badge bg-secondary">Full</span>'
                    }
                    <button class="btn btn-outline-primary btn-sm ms-2" onclick="showEventDetails(${event.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

async function registerForEvent(eventId) {
    try {
        const result = await apiCall('/register/', 'POST', {
            student_id: currentStudent.id,
            event_id: eventId
        });
        
        if (result) {
            showAlert('Successfully registered for the event!', 'success');
            loadEvents();
            loadMyEvents();
            loadHomeData();
        }
    } catch (error) {
        console.error('Error registering for event:', error);
    }
}

async function showEventDetails(eventId) {
    try {
        const event = await apiCall(`/events/${eventId}`);
        if (!event) return;
        
        const modal = document.getElementById('eventDetailsModal');
        const title = document.getElementById('eventModalTitle');
        const body = document.getElementById('eventModalBody');
        const footer = document.getElementById('eventModalFooter');
        
        title.textContent = event.title;
        
        const isRegistered = myRegistrations.some(r => r.event_id === event.id);
        const canRegister = event.status === 'active' && event.current_registrations < event.max_capacity && !isRegistered;
        
        body.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <h6>Event Details</h6>
                    <p>${event.description || 'No description available'}</p>
                    
                    <div class="row mb-3">
                        <div class="col-6">
                            <strong>Start Time:</strong><br>
                            <small class="text-muted">${new Date(event.start_time).toLocaleString()}</small>
                        </div>
                        <div class="col-6">
                            <strong>End Time:</strong><br>
                            <small class="text-muted">${new Date(event.end_time).toLocaleString()}</small>
                        </div>
                    </div>
                    
                    ${event.location ? `
                        <div class="mb-3">
                            <strong>Location:</strong><br>
                            <small class="text-muted">${event.location}</small>
                        </div>
                    ` : ''}
                    
                    <div class="mb-3">
                        <strong>Event Type:</strong>
                        <span class="badge bg-primary ms-2">${event.event_type}</span>
                    </div>
                </div>
                <div class="col-md-4">
                    <h6>Registration Info</h6>
                    <div class="mb-3">
                        <div class="d-flex justify-content-between">
                            <span>Capacity:</span>
                            <span>${event.current_registrations}/${event.max_capacity}</span>
                        </div>
                        <div class="capacity-bar mt-1">
                            <div class="capacity-fill" style="width: ${(event.current_registrations / event.max_capacity) * 100}%"></div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <strong>Status:</strong>
                        <span class="badge bg-${event.status === 'active' ? 'success' : 'secondary'} ms-2">${event.status}</span>
                    </div>
                </div>
            </div>
        `;
        
        footer.innerHTML = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            ${isRegistered ? 
                '<span class="badge bg-info me-2">Already Registered</span>' :
                canRegister ?
                    `<button type="button" class="btn btn-primary" onclick="registerForEvent(${event.id}); bootstrap.Modal.getInstance(document.getElementById('eventDetailsModal')).hide();">
                        <i class="fas fa-plus me-1"></i> Register Now
                    </button>` :
                    '<span class="badge bg-secondary">Event Full</span>'
            }
        `;
        
        new bootstrap.Modal(modal).show();
    } catch (error) {
        console.error('Error loading event details:', error);
    }
}

// My Events section functions
async function loadMyEvents() {
    try {
        const registrations = await apiCall(`/register/?student_id=${currentStudent.id}`);
        if (registrations) {
            myRegistrations = registrations;
            displayMyEvents(registrations);
        }
    } catch (error) {
        console.error('Error loading my events:', error);
    }
}

async function displayMyEvents(registrations) {
    const container = document.getElementById('my-events-list');
    container.innerHTML = '';
    
    if (registrations.length === 0) {
        container.innerHTML = '<div class="text-center py-5"><p class="text-muted">You haven\'t registered for any events yet</p></div>';
        return;
    }
    
    for (const registration of registrations) {
        try {
            const event = await apiCall(`/events/${registration.event_id}`);
            if (event) {
                const eventCard = createMyEventCard(event, registration);
                container.appendChild(eventCard);
            }
        } catch (error) {
            console.error('Error loading event for registration:', error);
        }
    }
}

function createMyEventCard(event, registration) {
    const card = document.createElement('div');
    card.className = 'event-card card mb-3';
    
    const now = new Date();
    const eventStart = new Date(event.start_time);
    const eventEnd = new Date(event.end_time);
    const isUpcoming = eventStart > now;
    const isOngoing = eventStart <= now && eventEnd >= now;
    const isPast = eventEnd < now;
    
    card.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <h6 class="card-title mb-0">${event.title}</h6>
                <span class="badge bg-${isUpcoming ? 'primary' : isOngoing ? 'success' : 'secondary'}">
                    ${isUpcoming ? 'Upcoming' : isOngoing ? 'Ongoing' : 'Past'}
                </span>
            </div>
            
            <div class="row mb-2">
                <div class="col-6">
                    <small class="text-muted">
                        <i class="fas fa-calendar me-1"></i>
                        ${new Date(event.start_time).toLocaleDateString()}
                    </small>
                </div>
                <div class="col-6">
                    <small class="text-muted">
                        <i class="fas fa-clock me-1"></i>
                        ${new Date(event.start_time).toLocaleTimeString()}
                    </small>
                </div>
            </div>
            
            ${event.location ? `
                <div class="mb-2">
                    <small class="text-muted">
                        <i class="fas fa-map-marker-alt me-1"></i>
                        ${event.location}
                    </small>
                </div>
            ` : ''}
            
            <div class="d-flex justify-content-between align-items-center">
                <small class="text-muted">Registered: ${new Date(registration.registered_at).toLocaleDateString()}</small>
                <div>
                    ${isPast ? 
                        `<button class="btn btn-outline-primary btn-sm" onclick="showFeedbackModal(${event.id})">
                            <i class="fas fa-star me-1"></i> Give Feedback
                        </button>` :
                        '<span class="text-muted">Event not yet completed</span>'
                    }
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// Feedback section functions
async function loadMyFeedback() {
    try {
        const feedback = await apiCall(`/feedback/?student_id=${currentStudent.id}`);
        if (feedback) {
            myFeedback = feedback;
            displayMyFeedback(feedback);
        }
    } catch (error) {
        console.error('Error loading my feedback:', error);
    }
}

async function displayMyFeedback(feedbackList) {
    const container = document.getElementById('feedback-list');
    container.innerHTML = '';
    
    if (feedbackList.length === 0) {
        container.innerHTML = '<div class="text-center py-5"><p class="text-muted">You haven\'t given any feedback yet</p></div>';
        return;
    }
    
    for (const feedback of feedbackList) {
        try {
            const registration = await apiCall(`/register/${feedback.registration_id}`);
            if (registration) {
                const event = await apiCall(`/events/${registration.event_id}`);
                if (event) {
                    const feedbackCard = createFeedbackCard(event, feedback);
                    container.appendChild(feedbackCard);
                }
            }
        } catch (error) {
            console.error('Error loading feedback details:', error);
        }
    }
}

function createFeedbackCard(event, feedback) {
    const card = document.createElement('div');
    card.className = 'card mb-3';
    
    card.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <h6 class="card-title mb-0">${event.title}</h6>
                <div class="rating-stars">
                    ${Array.from({length: 5}, (_, i) => 
                        `<i class="fas fa-star ${i < feedback.rating ? '' : 'text-muted'}"></i>`
                    ).join('')}
                </div>
            </div>
            
            <div class="mb-2">
                <small class="text-muted">
                    <i class="fas fa-calendar me-1"></i>
                    ${new Date(event.start_time).toLocaleDateString()}
                </small>
            </div>
            
            ${feedback.comment ? `
                <p class="card-text">${feedback.comment}</p>
            ` : ''}
            
            <small class="text-muted">
                Submitted: ${new Date(feedback.submitted_at).toLocaleString()}
            </small>
        </div>
    `;
    
    return card;
}

// Feedback modal functions
function showFeedbackModal(eventId) {
    const modal = document.getElementById('feedbackModal');
    document.getElementById('feedbackEventId').value = eventId;
    document.getElementById('feedbackRating').value = 0;
    document.getElementById('feedbackComment').value = '';
    
    // Reset star ratings
    document.querySelectorAll('.rating-star').forEach(star => {
        star.classList.remove('text-warning');
        star.classList.add('text-muted');
    });
    
    new bootstrap.Modal(modal).show();
}

function initializeRatingStars() {
    document.querySelectorAll('.rating-star').forEach(star => {
        star.addEventListener('click', function() {
            const rating = parseInt(this.dataset.rating);
            document.getElementById('feedbackRating').value = rating;
            
            // Update star display
            document.querySelectorAll('.rating-star').forEach((s, index) => {
                if (index < rating) {
                    s.classList.remove('text-muted');
                    s.classList.add('text-warning');
                } else {
                    s.classList.remove('text-warning');
                    s.classList.add('text-muted');
                }
            });
        });
        
        star.addEventListener('mouseenter', function() {
            const rating = parseInt(this.dataset.rating);
            document.querySelectorAll('.rating-star').forEach((s, index) => {
                if (index < rating) {
                    s.classList.remove('text-muted');
                    s.classList.add('text-warning');
                } else {
                    s.classList.remove('text-warning');
                    s.classList.add('text-muted');
                }
            });
        });
    });
    
    // Reset on mouse leave
    document.querySelector('.rating-input').addEventListener('mouseleave', function() {
        const currentRating = parseInt(document.getElementById('feedbackRating').value);
        document.querySelectorAll('.rating-star').forEach((s, index) => {
            if (index < currentRating) {
                s.classList.remove('text-muted');
                s.classList.add('text-warning');
            } else {
                s.classList.remove('text-warning');
                s.classList.add('text-muted');
            }
        });
    });
}

async function submitFeedback() {
    const eventId = document.getElementById('feedbackEventId').value;
    const rating = parseInt(document.getElementById('feedbackRating').value);
    const comment = document.getElementById('feedbackComment').value;
    
    if (rating === 0) {
        showAlert('Please select a rating', 'warning');
        return;
    }
    
    try {
        // Find the registration for this event
        const registration = myRegistrations.find(r => r.event_id === parseInt(eventId));
        if (!registration) {
            showAlert('Registration not found', 'error');
            return;
        }
        
        const result = await apiCall('/feedback/', 'POST', {
            registration_id: registration.id,
            rating: rating,
            comment: comment
        });
        
        if (result) {
            showAlert('Feedback submitted successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('feedbackModal')).hide();
            loadMyFeedback();
            loadHomeData();
        }
    } catch (error) {
        console.error('Error submitting feedback:', error);
    }
}

// QR Code functions
function showQRCode() {
    const modal = document.getElementById('qrCodeModal');
    const container = document.getElementById('qr-code-container');
    
    // Show loading spinner
    container.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Generating QR Code...</span>
        </div>
    `;
    
    new bootstrap.Modal(modal).show();
    
    // Generate QR code
    const qrData = JSON.stringify({
        student_id: currentStudent.student_id,
        student_name: currentStudent.name,
        college_id: currentStudent.college_id
    });
    
    QRCode.toCanvas(container, qrData, {
        width: 200,
        height: 200,
        color: {
            dark: '#000000',
            light: '#FFFFFF'
        }
    }, function(error) {
        if (error) {
            container.innerHTML = '<p class="text-danger">Error generating QR code</p>';
        }
    });
}

// Filter functions
function filterEvents() {
    const searchTerm = document.getElementById('event-search').value.toLowerCase();
    const typeFilter = document.getElementById('event-type-filter').value;
    
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
    
    displayEvents(filteredEvents);
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

// Placeholder functions
function showProfile() {
    showAlert('Profile functionality coming soon!', 'info');
}

function showSettings() {
    showAlert('Settings functionality coming soon!', 'info');
}

function logout() {
    showAlert('Logout functionality coming soon!', 'info');
}
