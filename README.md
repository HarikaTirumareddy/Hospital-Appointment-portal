# Hospital & Patient Appointment Management Portal

A full-stack, responsive web application built with **Python 3.11+**, **Django 5.x**, **Bootstrap 5**, and **SQLite**. Designed for college project evaluation and production readiness with **WhiteNoise** and **Gunicorn**.

---

## 🌟 Key Features

1. **Hospital Information Portal & Home Page**
   - Modern, medical-themed landing page with emergency helpline, department highlights, doctor cards, and live metrics.
2. **Specialist Doctor Directory**
   - Pre-loaded with **Cardiology**, **Pediatrics**, **Orthopedics**, **Neurology**, General Medicine, and Dermatology departments.
3. **Instant JavaScript Filtering (ES6+)**
   - Real-time client-side filtering by department buttons and instant keyword search by doctor name/specialty without page reload.
4. **Patient Authentication & Profile Management**
   - Secure patient registration with full name, email, phone, gender, blood group, date of birth, residential address, and emergency contact.
   - Session-based login/logout with CSRF protection and Django password validation.
5. **Conflict-Free Appointment Booking**
   - Patients can select doctor, date, and preferred time slot.
   - Interactive real-time slot checker via AJAX/fetch API disables booked slots in the browser.
6. **Strict Double-Booking Prevention Engine**
   - Guaranteed slot exclusivity at both the **Django Model layer (`clean()` validation)** and **Database layer (`UniqueConstraint`)**.
   - If an appointment is cancelled, the slot is automatically freed for other patients.
7. **Patient Self-Service Dashboard**
   - Organizes upcoming scheduled appointments, past consultation history, medical reports, and profile editing.
8. **Appointment Lifecycle Statuses**
   - Explicit tracking across four standard states: **Pending**, **Confirmed**, **Completed**, and **Cancelled** with color-coded badges.
9. **Staff & Administration Operations Portal**
   - Dedicated dashboard (`/staff/`) for hospital staff to manage appointment statuses, view daily metrics, and add/edit doctors.
   - Full integration with customized **Django Admin** (`/admin/`).
10. **Electronic Medical Records & Reports**
    - Hospital staff can issue clinical diagnoses, prescriptions, and upload lab reports linked to patient visits.
    - Patients can view and print official hospital letterhead reports (`window.print()`) or download attached files.
11. **Responsive Bootstrap 5 Design**
    - Clean medical teal/navy palette, micro-animations, mobile offcanvas navigation, and accessible forms.
12. **Deployment Ready**
    - Static file optimization via **WhiteNoise**.
    - Pre-configured `requirements.txt`, `Procfile`, and `runtime.txt` for platforms like Render, Railway, or Heroku.

---

## 🏗️ Project Architecture

```text
Hospital-Appointment-portal/
├── hospital_portal/           # Core Project Configuration
│   ├── settings.py           # Configured for WhiteNoise, Static/Media, Auth
│   ├── urls.py               # Main URL Routing & Admin Site Configuration
│   ├── wsgi.py               # WSGI Entry Point for Gunicorn
│   └── asgi.py               # ASGI Entry Point
├── portal/                   # Main Hospital Application
│   ├── models.py             # Department, Doctor, PatientProfile, Appointment, MedicalReport
│   ├── forms.py              # Forms with Double-Booking Validation
│   ├── views.py              # Public, Patient, API, and Staff Views
│   ├── urls.py               # Clean Named Routes
│   ├── admin.py              # Customized Django Admin Panels
│   ├── tests.py              # Automated Unit Test Suite
│   └── management/
│       └── commands/
│           └── seed_data.py  # Realistic Hospital Seed Data Generator
├── static/
│   ├── css/style.css         # Modern Medical Theme & Print Stylesheet
│   └── js/main.js            # Live Filter, Slot Checker, & Demo Autofill
├── templates/
│   ├── base.html             # Common Layout, Header, Messages, & Footer
│   └── portal/               # Application Templates
│       ├── home.html
│       ├── doctor_list.html
│       ├── doctor_detail.html
│       ├── login.html
│       ├── register.html
│       ├── patient_dashboard.html
│       ├── profile_edit.html
│       ├── book_appointment.html
│       ├── cancel_appointment_confirm.html
│       ├── report_detail.html
│       ├── staff_dashboard.html
│       ├── staff_doctors.html
│       ├── staff_doctor_form.html
│       ├── staff_doctor_delete_confirm.html
│       └── staff_report_form.html
├── media/                    # Uploaded Doctor Images & Medical Reports
├── staticfiles/              # WhiteNoise Collected Production Assets
├── db.sqlite3                # SQLite Database File
├── requirements.txt          # Python Dependencies
├── Procfile                  # Production Process File
├── runtime.txt               # Python Runtime Version
└── manage.py                 # Django Command-Line Utility
```

---

## 🔑 Pre-Configured Demo Credentials

The database has been pre-seeded with sample data for demonstration:

| Role | Username | Password | Access |
|---|---|---|---|
| **Hospital Admin / Staff** | `admin` | `adminpassword123` | Staff Portal (`/staff/`) & Django Admin (`/admin/`) |
| **Demo Patient** | `john_patient` | `patientpassword123` | Patient Dashboard (`/dashboard/`) & Booking |

> **Note**: The login page includes convenient **"Quick-Fill Demo Credentials"** buttons for one-click testing during project presentations.

---

## 🚀 How to Run Locally (Step-by-Step)

### Prerequisites
- Python 3.11 or higher installed on your system.

### Step 1: Open Terminal in Project Directory
Open PowerShell or Command Prompt in the project folder:
```powershell
cd c:\Users\DELL\Desktop\Hospital-Appointment-portal
```

### Step 2: Activate the Virtual Environment
- **On Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(If execution policy restricts scripts, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first)*
- **On Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```

### Step 3: Run Database Migrations (if needed)
```bash
python manage.py migrate
```

### Step 4: Seed Sample Data (Optional / Already Done)
If you ever want to re-populate the sample doctors, departments, and demo appointments:
```bash
python manage.py seed_data
```

### Step 5: Start the Development Server
```bash
python manage.py runserver
```

### Step 6: Access the Application
Open your web browser and navigate to:
- **Home Page:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Doctor Directory:** [http://127.0.0.1:8000/doctors/](http://127.0.0.1:8000/doctors/)
- **Patient Login:** [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
- **Patient Dashboard:** [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
- **Staff Operations Dashboard:** [http://127.0.0.1:8000/staff/](http://127.0.0.1:8000/staff/)
- **Django Admin Interface:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Running Automated Unit Tests
To verify all models, authentication, conflict prevention, and views:
```bash
python manage.py test
```
All 8 automated test suites verify that double booking is strictly prevented, cancellations restore slot availability, and security permissions are enforced.

---

## 🌐 Deployment Guide for Render (Step-by-Step)

The project is fully pre-configured for **Render** using:
- **`build.sh`**: Installs dependencies, runs migrations, seeds sample doctors, and collects static files.
- **`render.yaml`**: Declarative Blueprint specification for 1-click automatic provisioning.
- **`Procfile`**: Defines the Gunicorn WSGI process.
- **`runtime.txt`**: Specifies Python 3.11.9 runtime.
- **`hospital_portal/settings.py`**: Configured with `CSRF_TRUSTED_ORIGINS`, `RENDER_EXTERNAL_HOSTNAME`, and WhiteNoise storage.

---

### Option A: Automatic Deployment via Render Blueprint (Recommended)

1. **Push this project to a GitHub repository**:
   ```bash
   git init
   git add .
   git commit -m "Hospital Portal initial commit"
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
2. Log in to [Render.com](https://render.com).
3. Click **"New +"** &rarr; Select **"Blueprint"**.
4. Connect your GitHub repository.
5. Render will automatically read [`render.yaml`](render.yaml), set up the build command (`./build.sh`), start command (`gunicorn hospital_portal.wsgi:application`), generate a secure `SECRET_KEY`, and deploy the web service!

---

### Option B: Manual Web Service Deployment on Render

If you prefer setting up the web service manually:

1. **Push your code to GitHub** (same as above).
2. Go to [Render Dashboard](https://dashboard.render.com/) &rarr; Click **"New +"** &rarr; Select **"Web Service"**.
3. Select your repository.
4. Fill in the following settings:
   - **Name:** `hospital-appointment-portal` (or your choice)
   - **Region:** Any (e.g., Oregon / Ohio / Frankfurt)
   - **Branch:** `main`
   - **Root Directory:** *(leave blank)*
   - **Runtime:** `Python`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn hospital_portal.wsgi:application`
   - **Instance Type:** `Free`
5. Click **"Advanced"** &rarr; Add **Environment Variables**:
   - `PYTHON_VERSION` = `3.11.9`
   - `DEBUG` = `False`
   - `SECRET_KEY` = *(click "Generate" or type a random 50-character string)*
   - `RENDER` = `true`
6. Click **"Create Web Service"**.

---

### What Happens During Render Build:
During the build, Render automatically runs `build.sh`:
1. `pip install -r requirements.txt` &mdash; Installs Django, Gunicorn, WhiteNoise, and Pillow.
2. `python manage.py collectstatic --no-input` &mdash; Prepares and hashes all CSS/JS assets for WhiteNoise.
3. `python manage.py migrate` &mdash; Sets up the SQLite database schema.
4. `python manage.py seed_data` &mdash; Automatically creates the departments, doctors, demo patient (`john_patient`), and admin (`admin`) accounts!
5. Gunicorn starts the server and your app is live at `https://<your-service-name>.onrender.com`.

---

## 🧪 Running Automated Unit Tests
To verify all models, authentication, conflict prevention, and views:
```bash
python manage.py test
```
All 11 automated test suites verify that double booking is strictly prevented, cancellations restore slot availability, and security permissions are enforced.

