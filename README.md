# Django Table Reservation System

A comprehensive Django-based web application designed to manage table reservations, customers, table configurations, payments, and reservation audit logs for a restaurant or venue.

## Features

- **Customer Management**: Complete CRUD operations for customer profiles, storing contact info (email, phone, etc.).
- **Table & Category Configuration**: Manage tables, their seating capacity, location, active status, and classify them under categories (e.g., VIP, Outdoor, Standard).
- **Reservation Lifecycle**:
  - Book tables for specific dates, times, and guest counts.
  - Track reservation status (e.g., Booked, Confirmed, Cancelled).
  - Prevent double bookings and manage capacity.
- **Payment Integration Tracking**: Record and track payments associated with reservations, supporting states like Pending, Paid, Failed, and Refunded.
- **Audit Logging**: Automatic system-wide logging of reservation edits, cancellations, and creation details, preserving a history of changes.

## Tech Stack

- **Backend**: Python, Django
- **Database**: SQLite (default configuration)
- **Frontend Templates**: Django HTML Templates

## Project Structure

```text
├── config/                  # Django project configuration settings and routing
├── reservation_app/          # Core application containing models, views, forms, and templates
│   ├── models.py            # Database schema (Customer, Table, Reservation, Payment, AuditLog, etc.)
│   ├── views.py             # View controllers and business logic
│   ├── urls.py              # Application-specific URL routing
│   ├── forms.py             # Django forms for validation and user inputs
│   └── templates/           # HTML templates for the user interface
├── manage.py                # Django CLI management utility
└── db.sqlite3               # SQLite database file
```

## Setup & Installation

1. **Activate the Virtual Environment**:
   - On Windows:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

2. **Apply Migrations**:
   Run migrations to set up the database tables:
   ```bash
   python manage.py migrate
   ```

3. **Create a Superuser** (optional, for accessing the admin panel):
   ```bash
   python manage.py createsuperuser
   ```

4. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Open your browser and navigate to `http://127.0.0.1:8000/` to use the application or `http://127.0.0.1:8000/admin/` for Django Administration.