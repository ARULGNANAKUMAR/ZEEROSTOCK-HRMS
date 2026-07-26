# Human Resource Management System (HRMS)

## Full Stack Developer Technical Assignment

**Candidate:** ARUL GNANAKUMAR

**Position:** Full Stack Developer

**Company:** Zeerostock Ventures

---

# Project Overview

The Human Resource Management System (HRMS) is a web-based application developed to simplify and automate core human resource operations. The system enables HR administrators to manage employees, attendance records, leave requests, and user authentication through a clean and responsive interface.

The application follows a client-server architecture where the frontend communicates with the backend using REST APIs. The project has been developed with modularity, maintainability, and scalability in mind while demonstrating the fundamentals of full stack development.

---

# Objectives

The primary objectives of this project are:

- Develop a secure authentication system.
- Manage employee information.
- Track employee attendance.
- Manage leave requests.
- Implement role-based access control.
- Demonstrate frontend and backend integration using REST APIs.

---

# Features

## Authentication

- Secure Login
- Logout
- Session Management
- Password Hashing
- Role-Based Access Control

---

## HR Module

- HR Dashboard
- Employee Management
- Add Employee
- Edit Employee
- Employee Search
- Attendance Management
- Leave Request Management
- Dashboard Statistics

---

## Employee Module

The project includes the initial implementation and architecture for employee-side functionality.

Implemented features include:

- Employee Dashboard
- Profile Management
- Attendance View
- Leave View

Additional employee self-service features are planned for future development.

---

# Technology Stack

## Frontend

- HTML5
- CSS3
- Vanilla JavaScript

## Backend

- Python
- Flask

## Database

- SQLite

## API

- RESTful APIs

## Authentication

- Session-Based Authentication
- Secure Password Hashing

## Development Tools

- Visual Studio Code
- Git
- GitHub
- Postman

---

# Project Structure

```
HRMS
│
├── static/
│   ├── css/
│   ├── js/
│   └── assets/
│
├── templates/
│
├── app.py
│
├── database.db
│
├── requirements.txt
│
└── README.md
```

---

# Application Workflow

```
Browser

↓

HTML5 + CSS3 + JavaScript

↓

REST API

↓

Python Flask

↓

SQLite Database
```

---

# Authentication Flow

```
User Login

↓

Credential Validation

↓

Password Verification

↓

Session Creation

↓

Protected Dashboard

↓

Logout
```

---

# Functional Modules

## HR

- Dashboard
- Employee Management
- Attendance
- Leave Management
- User Management

## Employee

- Dashboard
- Attendance
- Leave
- Profile

---

# Database

The application uses SQLite as the primary database.

Main tables include:

- Users
- Employees
- Attendance
- Leave Requests
- Notifications

The database is lightweight and suitable for development and technical assignment purposes.

---

# API Overview

The application exposes REST APIs for frontend communication.

Examples include:

```
POST /login

GET /hr/dashboard

GET /hr/employees

POST /hr/employees/add

PUT /hr/employees/update

DELETE /hr/employees/delete

GET /attendance

POST /attendance/checkin

POST /attendance/checkout

GET /leaves

POST /leaves/apply
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/ARULGNANAKUMAR/ZEEROSTOCK-HRMS.git
```

Move into the project directory

```bash
cd ZEEROSTOCK-HRMS
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

# Testing

The application was tested using:

- Manual Functional Testing
- Browser Testing
- API Testing using Postman

The following modules were verified:

- Login
- Logout
- Employee CRUD
- Attendance
- Leave Management
- API Responses
- Form Validation

---

# Challenges Faced

During development, the following technical challenges were encountered:

- Designing role-based authentication.
- Integrating frontend with backend REST APIs.
- Managing API routing.
- Debugging authentication flow.
- Connecting frontend forms with backend services.
- Maintaining clean JavaScript modules.

Each issue was resolved through debugging, testing, and incremental improvements.

---

# AI Assistance

Artificial Intelligence tools were used as development assistants during this project.

### DeepSeek

Used for:

- Backend code generation
- JavaScript implementation
- REST API structure
- Authentication boilerplate

### ChatGPT

Used for:

- Understanding project architecture
- API concepts
- Authentication workflow
- Documentation preparation
- Code review
- Technical explanations

### Blackbox AI

Used for:

- Debugging
- Code correction
- Error fixing
- Code optimization

All generated code was reviewed, modified, integrated, tested, and validated before being included in the final implementation.

The frontend interface, project integration, customization, debugging, testing, and final submission were completed by the developer.

---

# Future Improvements

The following enhancements are planned:

- Complete Employee Self-Service Portal
- Payroll Management
- Email Notifications
- Dashboard Analytics
- Charts and Reports
- Mobile Responsive Improvements
- Face Recognition Attendance
- File Upload Support
- Multi-Department Management
- Cloud Deployment
- Audit Logs

---

# Repository

GitHub Repository

```
https://github.com/ARULGNANAKUMAR/ZEEROSTOCK-HRMS
```

---

# License

This project was developed as part of a Full Stack Developer Technical Assignment for Zeerostock Ventures.

This repository is intended for evaluation purposes only.

---

# Declaration

I hereby declare that this project was developed as part of the technical assignment. Artificial Intelligence tools were used to assist with learning, code generation, debugging, and documentation. All generated code was reviewed, customized, integrated, tested, and validated before submission. The final implementation reflects my understanding of the application architecture, frontend development, backend integration, authentication, API communication, and overall system workflow.
