
# Octina

**Octina** is a full-stack workforce attendance and HR management platform built with Django for organizations that need structured employee tracking, location-based check-in verification, shift management, payroll calculation, absence monitoring, vacation workflows, and reporting in one centralized system.

It is designed as a production-oriented internal management tool for companies where attendance accuracy, supervisory control, and monthly payroll visibility matter.

---

## Highlights

- Attendance tracking with start / stop session flow
- GPS-based location verification for staff and users
- Shift scheduling and delay detection
- Payroll and income calculation
- Vacation request and approval workflow
- Absence, warning, and non-progress tracking
- Excel report export for individual and team records
- Jalali calendar support
- Role-based access and hierarchical ownership model
- Server-rendered Django architecture with modular app boundaries

---

## Tech Stack

- Python
- Django
- Django REST Framework
- OpenPyXL
- GeoPy
- Jdatetime
- django-cors-headers
- drf-yasg
- HTML
- CSS
- JavaScript

---

## What Octina Does

Octina helps organizations manage their daily workforce operations through a single system that combines:

- employee profiles
- staff hierarchy
- attendance recording
- work hour calculation
- monthly income generation
- shift policies
- holiday handling
- location validation
- warning generation
- vacation management
- administrative reporting

The platform is especially useful for businesses that need to track staff presence, calculate working time, and generate structured reports without relying on manual spreadsheets.

---

## Core Features

### Attendance Management
- Start and end attendance sessions
- Track whether an employee is currently in progress
- Calculate work duration automatically
- Preserve session history and time ranges
- Support multi-session attendance records

### Location Verification
- Register staff location
- Register user location
- Compare live coordinates with the reference location
- Validate presence within a proximity threshold
- Use geodesic distance calculation for accuracy

### Shift Management
- Create and manage shift work definitions
- Assign working days
- Detect lateness based on current shift time
- Detect overtime conditions
- Support staff-specific work schedules

### Payroll and Income
- Create monthly income records
- Calculate income based on working time and position
- Support both hourly and monthly compensation logic
- Generate monthly attendance-income summaries

### Warnings and Absences
- Track delay warnings
- Create absence-related records
- Store user notifications
- Monitor users with no confirmation
- Review all historical warnings

### Vacation Workflow
- Submit vacation requests
- Attach vacation records to user profiles
- Manager approval / rejection flow
- Track confirmed and unconfirmed vacations

### Reporting
- Export individual attendance data to Excel
- Export organizational attendance and income reports
- Show monthly and yearly breakdowns
- Present user-level work time and salary summaries

### Administrative Management
- Create users for staff members
- Create and manage profiles
- Create and manage positions
- Create and manage holidays
- View attendance status by month and year
- Review incomplete progress records
- Filter user and salary data

---

## Architecture Overview

Octina follows a modular Django structure with separate areas for:

- `home` for public marketing pages
- `Attendance` for employee attendance flows
- `managing` for staff administration
- `locations` for GPS handling
- `price` for pricing / payroll-related workflow

The application uses custom ownership logic such as `created_who` and `created_by` to isolate data between staff and the users they manage.

### Main flow

```text
User / Staff Action
        ↓
Django View
        ↓
Model / Business Logic
        ↓
Attendance, Location, Payroll, or Warning Processing
        ↓
Rendered Template or Excel Export
```

---

## Key Modules

### 1. Location Module

Handles GPS setup and verification.

* staff location registration
* user location capture
* geodesic distance calculation
* attendance confirmation based on distance threshold

### 2. Attendance Module

Handles the attendance lifecycle.

* create attendance record
* start attendance session
* end attendance session
* calculate job time
* manage delay and overtime
* show results and summaries

### 3. Managing Module

Handles all administrative operations.

* user management
* shift management
* position management
* profile management
* holiday management
* absence review
* vacation approval
* confirmation review
* export reports

### 4. Home Module

Public-facing informational pages.

* landing page
* about page
* services page
* team page
* why-us page
* slider details page

### 5. Price Module

Payroll-related route for pricing / processing flow.

---

## Attendance Logic

Octina supports a complete attendance lifecycle:

1. An attendance record is created or reused.
2. The employee checks location if required.
3. The system determines whether the user is within the allowed radius.
4. Attendance is confirmed or rejected based on location rules.
5. Working start and end times are stored.
6. Job duration is calculated.
7. The result is used for salary and report generation.

### Supported status checks

* in progress
* confirmation status
* delay status
* overtime status
* holiday check

---

## Location Verification Logic

Octina includes a proximity check that compares the user location with a manager-defined reference location.

* staff registers an active location
* user submits current latitude and longitude
* system calculates distance using geodesic math
* if the distance is within the accepted threshold, confirmation can be granted
* otherwise attendance can be marked as not confirmed

This makes the project more than a basic attendance app. It adds a real-world verification layer.

---

## Payroll Logic

Salary calculation is tied to the attendance system.

* working time is measured
* position income is retrieved
* monthly or hourly logic is applied
* total payment is calculated
* monthly `Income` records are created or reused

This lets Octina function as a lightweight payroll engine instead of only an attendance tracker.

---

## Warnings and Absence Tracking

The system tracks workforce behavior through:

* delay records
* absence records
* non-progress records
* warning notifications

This is useful for HR teams and supervisors who need visibility over attendance quality, not just attendance presence.

---

## Vacation Management

Employees can request vacations, and managers can review them.

* vacation request creation
* linkage to user profile
* approval by employer
* rejection workflow
* vacation list review

---

## Reports and Export

Octina supports Excel exports for both individual and organization-wide reports.

### Export types

* user attendance report
* monthly salary report
* company-wide user summary
* missing-income user highlighting

This makes it easy to move from digital records to management-ready spreadsheets.

---

## Routes and Functional Areas

### Public / Home

* `/`
* `/about/`
* `/services/`
* `/team/`
* `/why-us/`
* `/slider/readmore/`

### Attendance

* attendance session creation
* attendance result view
* attendance start / stop flow
* user warnings
* holiday list
* user reports
* absence records

### Managing

* user list
* user create / update / delete
* shift list / create / update / delete
* position list / create / update / delete
* profile list / create / update / delete
* holiday create / update / delete
* vacation review
* confirmation review
* exports

### Locations

* staff location setup
* user location check
* process location verification
* ignore location flow

### Price

* payroll / pricing processing route

---

## Data Model Concepts

The codebase is built around several key concepts:

* **CustomUser**: main user entity
* **Profile**: user job and position data
* **AttendanceUser**: attendance session model
* **Income**: payroll record
* **ShiftWork**: work schedule definition
* **Location**: GPS reference point
* **Holidays**: holiday definitions
* **Delay**: lateness records
* **Vacation**: vacation requests
* **AbsenceWarning**: warnings and alerts
* **AttendanceStatus**: attendance status logs
* **NoneInProgress**: non-progress tracking

---

## Access Control Philosophy

Octina uses hierarchical ownership patterns to separate organization data.

Typical rules:

* staff can manage users created under them
* users can only access their own attendance where appropriate
* managers can review team-level reports
* superusers can access wider system data
* custom decorators protect restricted views

---

## Project Strengths

* Real-world HR workflow coverage
* Attendance plus payroll in one system
* GPS-based verification
* Strong administrative tools
* Excel report generation
* Jalali calendar compatibility
* Modular Django structure
* Good foundation for a SaaS or internal HR platform

---

## Possible Improvements

* Refactor large views into service layers
* Introduce REST API endpoints for all management flows
* Add real-time notifications with WebSocket
* Split attendance and payroll into separate apps
* Add Docker support
* Add task queue support with Celery
* Add audit logging
* Add tests for critical attendance and payroll flows
* Normalize duplicate route and view definitions
* Move secrets and config values to environment variables

---

## Installation

```bash
git clone https://github.com/yourusername/octina.git
cd octina

python -m venv venv
source venv/bin/activate
# Windows:
# venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Environment Variables

Create a `.env` file and keep sensitive values out of version control.

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

If SMS or external services are used in your setup:

```env
GHASEDAK_API_KEY=your-api-key
FRONTEND_URL=https://your-domain.com
```

---

## Folder Structure

```text
project/
├── Attendance_app/
├── accounts/
├── home/
├── managing/
├── locations/
├── price/
├── templates/
├── static/
├── media/
├── manage.py
└── requirements.txt
```

---

## Screenshots

Add project screenshots here:

* dashboard
* attendance start page
* location verification page
* admin user list
* payroll report
* Excel export preview

---

## License

This project is available for portfolio and educational use.

---

## Author

Developed by **Amir Ali Sheibani**

GitHub: [https://github.com/AmirAliSheibani](https://github.com/AmirAliSheibani)


