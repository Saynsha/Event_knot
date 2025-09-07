# User Flow Diagrams

## Complete Student Journey

```mermaid
journey
    title Student Event Participation Journey
    section Discovery
      Browse Events: 5: Student
      Search Events: 4: Student
      View Event Details: 5: Student
    section Registration
      Register for Event: 5: Student
      Receive Confirmation: 4: Student
      Add to Calendar: 3: Student
    section Event Day
      Check-in at Event: 5: Student
      Participate in Event: 5: Student
      Check-out: 4: Student
    section Feedback
      Submit Feedback: 4: Student
      Rate Event: 5: Student
      View Past Feedback: 3: Student
```

## Admin Event Management Flow

```mermaid
flowchart TD
    A[Admin Login] --> B[Dashboard]
    B --> C{Action Required}
    
    C -->|Create Event| D[Event Creation Form]
    C -->|Manage Events| E[Event List]
    C -->|Track Attendance| F[Attendance Interface]
    C -->|View Reports| G[Reports Dashboard]
    
    D --> D1[Fill Event Details]
    D1 --> D2[Set Capacity & Timing]
    D2 --> D3[Save Event]
    D3 --> D4[Event Created Successfully]
    D4 --> B
    
    E --> E1[Select Event]
    E1 --> E2{Event Action}
    E2 -->|Edit| E3[Update Event Details]
    E2 -->|Cancel| E4[Cancel Event]
    E2 -->|View Stats| E5[Event Analytics]
    E3 --> E6[Event Updated]
    E4 --> E7[Event Cancelled]
    E5 --> E8[Show Statistics]
    E6 --> B
    E7 --> B
    E8 --> B
    
    F --> F1[Select Event]
    F1 --> F2[Show Registered Students]
    F2 --> F3{Check-in Method}
    F3 -->|Manual| F4[Search Student]
    F3 -->|QR Code| F5[Scan QR Code]
    F4 --> F6[Mark Attendance]
    F5 --> F6
    F6 --> F7[Update Attendance Record]
    F7 --> B
    
    G --> G1[Select Report Type]
    G1 --> G2[Apply Filters]
    G2 --> G3[Generate Report]
    G3 --> G4[View/Export Report]
    G4 --> B
```

## Registration Process Flow

```mermaid
sequenceDiagram
    participant S as Student
    participant UI as Student Interface
    participant API as Backend API
    participant DB as Database
    participant E as Email Service
    
    S->>UI: Click "Register for Event"
    UI->>API: POST /register/
    API->>DB: Check student exists
    DB-->>API: Student found
    API->>DB: Check event exists & active
    DB-->>API: Event found & active
    API->>DB: Check capacity
    DB-->>API: Capacity available
    API->>DB: Check duplicate registration
    DB-->>API: No duplicate found
    API->>DB: Create registration
    DB-->>API: Registration created
    API->>DB: Update event registration count
    DB-->>API: Count updated
    API->>E: Send confirmation email
    E-->>API: Email sent
    API-->>UI: Registration successful
    UI-->>S: Show confirmation message
```

## Attendance Tracking Flow

```mermaid
flowchart TD
    A[Event Starts] --> B[Admin Opens Attendance Interface]
    B --> C[Select Event]
    C --> D[Show Registered Students List]
    
    D --> E{Check-in Method}
    E -->|Manual Search| F[Search by Student ID/Name]
    E -->|QR Code Scan| G[Scan Student QR Code]
    E -->|Bulk Check-in| H[Select Multiple Students]
    
    F --> I[Find Student]
    G --> J[Decode QR Code]
    H --> K[Select Students to Check-in]
    
    I --> L{Student Found?}
    J --> M{Valid QR Code?}
    K --> N[Process Selected Students]
    
    L -->|Yes| O[Check Registration Status]
    L -->|No| P[Show Error Message]
    
    M -->|Yes| O
    M -->|No| Q[Invalid QR Code Error]
    
    O --> R{Already Checked In?}
    R -->|No| S[Mark as Present]
    R -->|Yes| T[Already Checked In Message]
    
    S --> U[Update Attendance Record]
    U --> V[Show Success Message]
    V --> D
    
    N --> W[Mark All Selected as Present]
    W --> U
    
    P --> D
    Q --> D
    T --> D
```

## Feedback Collection Flow

```mermaid
graph TD
    A[Event Ends] --> B[Student Opens App]
    B --> C[View Past Events]
    C --> D[Select Attended Event]
    D --> E{Feedback Already Submitted?}
    
    E -->|No| F[Show Feedback Form]
    E -->|Yes| G[Show Previous Feedback]
    
    F --> H[Rate Event 1-5 Stars]
    H --> I[Add Optional Comment]
    I --> J[Submit Feedback]
    J --> K[Validate Feedback]
    K --> L{Valid?}
    
    L -->|Yes| M[Save Feedback]
    L -->|No| N[Show Validation Error]
    
    M --> O[Show Thank You Message]
    O --> P[Update Event Rating]
    P --> Q[Feedback Submitted Successfully]
    
    N --> F
    G --> R[Allow Edit Feedback]
    R --> F
```

## Error Handling Flow

```mermaid
flowchart TD
    A[User Action] --> B[API Request]
    B --> C{Validation}
    C -->|Valid| D[Process Request]
    C -->|Invalid| E[Return Validation Error]
    
    D --> F{Business Logic}
    F -->|Success| G[Return Success Response]
    F -->|Failure| H[Check Error Type]
    
    H --> I{Error Type}
    I -->|Not Found| J[Return 404 Error]
    I -->|Duplicate| K[Return 400 Error]
    I -->|Capacity Full| L[Return 400 Error]
    I -->|Permission| M[Return 403 Error]
    I -->|Server Error| N[Return 500 Error]
    
    E --> O[Display Error to User]
    J --> O
    K --> O
    L --> O
    M --> O
    N --> P[Log Error & Show Generic Message]
    P --> O
    
    G --> Q[Update UI]
    O --> R[Allow User to Retry]
```

## System Architecture Flow

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Student Mobile App]
        B[Admin Web Portal]
        C[Public Event Browser]
    end
    
    subgraph "API Layer"
        D[FastAPI Application]
        E[Authentication Service]
        F[Rate Limiting]
    end
    
    subgraph "Business Logic Layer"
        G[Event Management]
        H[Registration Service]
        I[Attendance Tracking]
        J[Feedback Collection]
        K[Reporting Engine]
    end
    
    subgraph "Data Layer"
        L[SQLite Database]
        M[File Storage]
        N[Cache Layer]
    end
    
    subgraph "External Services"
        O[Email Service]
        P[QR Code Generator]
        Q[Analytics Service]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    D --> J
    D --> K
    
    G --> L
    H --> L
    I --> L
    J --> L
    K --> L
    
    D --> O
    D --> P
    D --> Q
```
