# Admin Portal Wireframes

## Admin Dashboard Overview

```mermaid
graph TD
    A[Admin Dashboard] --> B[Event Management]
    A --> C[Student Management]
    A --> D[Attendance Tracking]
    A --> E[Reports & Analytics]
    A --> F[System Settings]
    
    B --> G[Create Event]
    B --> H[Event List]
    B --> I[Event Details]
    B --> J[Event Analytics]
    
    C --> K[Student List]
    C --> L[Add Student]
    C --> M[Student Details]
    C --> N[Bulk Import]
    
    D --> O[Check-in Interface]
    D --> P[Attendance Reports]
    D --> Q[QR Code Scanner]
    
    E --> R[Registration Stats]
    E --> S[Attendance Reports]
    E --> T[Feedback Analysis]
    E --> U[Top Students]
```

## Event Creation Interface

```mermaid
graph LR
    subgraph "Event Creation Form"
        A[Event Title*]
        B[Description]
        C[Event Type*]
        D[Start Date/Time*]
        E[End Date/Time*]
        F[Location]
        G[Max Capacity*]
        H[College Selection*]
        I[Save Event]
    end
    
    subgraph "Event Type Options"
        J[Academic]
        K[Social]
        L[Sports]
        M[Workshop]
        N[Conference]
        O[Cultural]
    end
    
    subgraph "Validation Rules"
        P[End time > Start time]
        Q[Capacity > 0]
        R[Required fields filled]
        S[Unique event title]
    end
```

## Event Management Dashboard

```mermaid
graph TB
    subgraph "Event List Table"
        A[Event ID | Title | Type | Date | Capacity | Registrations | Status | Actions]
        B[001 | Tech Conference | Conference | 2024-03-15 | 200 | 150 | Active | Edit/View/Delete]
        C[002 | Sports Day | Sports | 2024-03-20 | 100 | 85 | Active | Edit/View/Delete]
        D[003 | Workshop | Workshop | 2024-03-10 | 50 | 50 | Completed | View/Reports]
    end
    
    subgraph "Filter Options"
        E[Filter by College]
        F[Filter by Event Type]
        G[Filter by Status]
        H[Filter by Date Range]
        I[Search by Title]
    end
    
    subgraph "Bulk Actions"
        J[Select All]
        K[Cancel Selected]
        L[Export to CSV]
        M[Send Notifications]
    end
```

## Attendance Tracking Interface

```mermaid
graph TD
    A[Attendance Dashboard] --> B[Event Selection]
    A --> C[Student Check-in]
    A --> D[Attendance Reports]
    
    B --> E[Select Event]
    E --> F[Show Registered Students]
    
    C --> G[Student Search/Scan]
    G --> H[Check-in Button]
    G --> I[Check-out Button]
    H --> J[Mark Present]
    I --> K[Mark Check-out]
    
    D --> L[Real-time Attendance]
    D --> M[Attendance Summary]
    D --> N[Export Attendance]
    
    subgraph "Check-in Methods"
        O[Manual Search]
        P[QR Code Scan]
        Q[Student ID Input]
        R[Bulk Check-in]
    end
```

## Reports & Analytics Dashboard

```mermaid
graph LR
    subgraph "Report Categories"
        A[Event Reports]
        B[Student Reports]
        C[Attendance Reports]
        D[Feedback Reports]
        E[System Reports]
    end
    
    subgraph "Event Reports"
        F[Event Popularity]
        G[Registration Trends]
        H[Capacity Utilization]
        I[Event Type Analysis]
    end
    
    subgraph "Student Reports"
        J[Most Active Students]
        K[Attendance Rates]
        L[Participation Trends]
        M[Student Engagement]
    end
    
    subgraph "Visualization Options"
        N[Charts & Graphs]
        O[Data Tables]
        P[Export Options]
        Q[Date Range Filters]
    end
```

## College Management Interface

```mermaid
graph TB
    subgraph "College List"
        A[College ID | Name | Location | Students | Events | Actions]
        B[001 | University A | New York | 500 | 25 | Edit/View/Stats]
        C[002 | College B | California | 300 | 15 | Edit/View/Stats]
    end
    
    subgraph "College Details"
        D[College Information]
        E[Student Management]
        F[Event Management]
        G[Performance Metrics]
    end
    
    subgraph "Bulk Operations"
        H[Import Students]
        I[Create Multiple Events]
        J[Send Notifications]
        K[Export Data]
    end
```

## System Settings Panel

```mermaid
graph LR
    subgraph "General Settings"
        A[System Name]
        B[Default Capacity]
        C[Event Types]
        D[Notification Settings]
    end
    
    subgraph "User Management"
        E[Admin Users]
        F[Permissions]
        G[Role Assignment]
        H[Access Control]
    end
    
    subgraph "Database Settings"
        I[Backup Settings]
        J[Data Retention]
        K[Export Options]
        L[Import Settings]
    end
```
