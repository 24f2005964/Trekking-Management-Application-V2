# Trekking Management Application (TMA) - V2

**Course:** Modern Application Development II (MAD 2)  
**Degree:** IIT Madras BS in Data Science and Applications  
**Student Name:** Hemant Singh Chauhan  
**Roll Number:** 24f2005964  
**Project Repository:** [24f2005964/Trekking-Management-Application-V2](https://github.com/24f2005964/Trekking-Management-Application-V2)

---

## 1. Project Overview

**Trekking Management Application (TMA V2)** is a comprehensive, production-grade web application designed for commercial trekking operators, licensed mountain guides, and outdoor enthusiasts. It facilitates the end-to-end lifecycle of high-altitude trekking expeditions: route creation, guide assignment, capacity management, atomic booking concurrency, automated daily reminders, asynchronous batch exports, and monthly executive analytics reports.

Built strictly according to **IIT Madras BS Degree MAD 2** coursework specifications as a decoupled architecture:
- **Backend:** Flask REST API with Flask-JWT-Extended role-based authorization, SQLite persistence via SQLAlchemy ORM, Redis multi-tier caching, and Celery asynchronous background task queues.
- **Frontend:** Responsive Vue 3 Single Page Application (SPA) powered by Vite, Pinia state management, Vue Router 4 route guards, Bootstrap 5, and Chart.js analytics visualization.

---

## 2. System Architecture

```text
+-----------------------------------------------------------------------+
|                    Vue 3 Single Page Application                      |
|          (Vite + Pinia + Vue Router + Bootstrap 5 + Chart.js)         |
+-----------------------------------+-----------------------------------+
                                    | REST API (JSON / JWT)
                                    v
+-----------------------------------------------------------------------+
|                           Flask REST API                              |
|           (Flask-JWT-Extended + RBAC Security Decorators)             |
+-------------------+-------------------------------+-------------------+
                    |                               |
          SQLAlchemy ORM (SQLite)          Task Broker & Cache (Redis)
                    |                               |
                    v                               v
+-----------------------+       +---------------------------------------+
|      SQLite DB        |       |             Redis Server              |
|  (tma_v2.db / Memory) |       |     (Cache TTL & Celery Broker)       |
+-----------------------+       +-------------------+-------------------+
                                                    |
                                    +---------------+---------------+
                                    |                               |
                                    v                               v
                    +-------------------------------+ +-------------------------------+
                    |         Celery Worker         | |          Celery Beat          |
                    | (CSV Export, PDF Generation,  | | (Daily Reminders @ 08:00 UTC, |
                    |  MIME Email Logging & Webhook)| |  Monthly Reports on 1st)      |
                    +-------------------------------+ +-------------------------------+
```

---

## 3. Technology Stack

| Component | Technology | Version / Specification | Role in Application |
|---|---|---|---|
| **Backend Framework** | Flask | 3.1.3 | RESTful API endpoints and SPA production asset serving |
| **ORM & Database** | SQLAlchemy / SQLite | 2.0 / 3.x | Relational persistence with cascade rules, transactions & foreign keys |
| **Authentication** | Flask-JWT-Extended | 4.7.1 | Stateless JWT authentication via HTTP headers & query strings |
| **Task Queue** | Celery | 5.6.3 | Asynchronous batch job worker and Celery Beat periodic scheduler |
| **Cache & Broker** | Redis | 7.0+ | Key-value caching layer (with TTL invalidation) and Celery message broker |
| **Frontend Framework** | Vue.js | 3.4 (Composition API) | Reactive Single Page Application |
| **Build Tool** | Vite | 5.4 | Bundler with chunk splitting and local proxy server |
| **State Management** | Pinia | 2.2 | Reactive store for authenticated user state and session tokens |
| **Client Routing** | Vue Router | 4.4 | Navigation with role-based navigation guards (`meta.requiresAuth`) |
| **UI Styling & Icons** | Bootstrap 5 & Icons | 5.3.3 / 1.11.3 | Responsive modern layout without native browser alerts |
| **Analytics Charts** | Chart.js & vue-chartjs | 4.4.4 / 5.3.1 | Visual expedition analytics, booking trends & difficulty charts |
| **PDF Engine** | ReportLab | 3.6.13 | Programmatic vector PDF generation for monthly management reports |
| **Testing Suite** | Pytest | 8.3.4 | Automated unit and integration test suite (18 test suites) |

---

## 4. Project Directory Structure

```text
Trekking-Management-Application-V2/
├── .gitignore                           # Git exclusion rules (venv, db, node_modules, logs)
├── README.md                            # Comprehensive project documentation
├── PROJECT_REPORT.md                    # IITM MAD 2 formal project submission report
├── requirements.txt                     # Python dependencies
├── run.sh                               # Unified one-click application runner
├── pyrefly.toml                         # Python toolchain configuration
├── pyrightconfig.json                   # Python type checking configuration
│
├── backend/                             # Flask REST API, SQLite, Redis, Celery
│   ├── run.py                           # Flask backend entry point (Port 5001)
│   ├── celery_worker.py                 # Celery worker & beat process runner
│   ├── pytest.ini                       # Pytest execution configuration
│   │
│   ├── app/                             # Core Flask application package
│   │   ├── __init__.py                  # Application factory, SPA serving & blueprint registry
│   │   ├── config.py                    # App configuration, JWT keys, and Redis URLs
│   │   ├── extensions.py                # Initialized extensions (db, jwt, cors, cache, celery)
│   │   ├── models.py                    # Database models (User, StaffProfile, Trek, Booking, etc.)
│   │   ├── seed.py                      # Programmatic database seeder (initial users & treks)
│   │   │
│   │   ├── api/                         # REST API Blueprint controllers
│   │   │   ├── auth.py                  # Register, login, me, logout
│   │   │   ├── admin.py                 # Admin dashboard, user management, trek CRUD, reports
│   │   │   ├── staff.py                 # Staff dashboard, slot adjustments, participant rosters
│   │   │   └── trekker.py               # Trek discovery, booking, cancellation, CSV export
│   │   │
│   │   ├── tasks/                       # Celery asynchronous tasks
│   │   │   ├── scheduled.py             # Periodic daily trek reminders & monthly activity reports
│   │   │   └── export.py                # Asynchronous user booking history CSV export
│   │   │
│   │   ├── services/                    # Business service layers
│   │   │   ├── email_service.py         # Multi-channel reminder dispatch (SMTP / Webhook / MIME log)
│   │   │   └── pdf_service.py           # Programmatic monthly vector PDF report generator
│   │   │
│   │   └── utils/                       # Shared helpers and decorators
│   │       ├── cache.py                 # Redis cache invalidation helper functions
│   │       └── decorators.py            # `@admin_required`, `@staff_required`, `@trekker_required`
│   │
│   ├── exports/                         # Output folder for generated CSVs, HTML & PDF reports
│   ├── uploads/                         # Storage for file uploads and participant documents
│   └── tests/                           # Pytest automated test suites (18/18 passing)
│       ├── conftest.py                  # Pytest fixtures, test database setup & JWT auth helpers
│       ├── test_admin_pdf_reports.py    # Tests for monthly ReportLab PDF & HTML generation
│       ├── test_admin_user_deletion.py  # Tests for safe user deletion and slot restoration
│       ├── test_auth.py                 # Tests for registration, login, JWT validation & RBAC
│       ├── test_booking_integrity.py    # Tests for atomic booking concurrency & slot capacity guards
│       ├── test_celery_tasks.py         # Tests for async CSV exports & eager task execution
│       ├── test_notifications_and_email.py # Tests for reminder dispatch channels & logging
│       └── test_reminders_and_schedule.py  # Tests for Celery Beat scheduled jobs
│
└── frontend/                            # Vue 3 SPA (Vite + Bootstrap 5 + Pinia)
    ├── index.html                       # Single Page Application HTML root
    ├── package.json                     # NPM packages & build scripts
    ├── vite.config.js                   # Vite config with dev proxy & chunk splitting
    ├── dist/                            # Production build (served directly by Flask)
    │
    └── src/
        ├── App.vue                      # Root layout component
        ├── main.js                      # Vue app bootstrapping & plugin injection
        ├── router/index.js              # Vue Router 4 with role-based auth guards
        ├── stores/auth.js               # Pinia store for JWT token and user authentication
        ├── services/api.js              # Axios HTTP client with JWT interceptor
        │
        ├── components/                  # Reusable UI components
        │   ├── Navbar.vue               # Global responsive navigation with role switching
        │   ├── StatusBadge.vue          # Color-coded badge for booking & expedition states
        │   ├── TrekCard.vue             # Card component for expedition catalog display
        │   └── AnalyticsChart.vue       # Reactive Chart.js wrapper for metrics & graphs
        │
        ├── views/                       # Role-specific application views
        │   ├── auth/                    # LoginView, RegisterView
        │   ├── admin/                   # AdminDashboard, AdminTreks, AdminUsers, AdminReports
        │   ├── staff/                   # StaffDashboard, TrekParticipants
        │   └── trekker/                 # TrekkerDashboard, MyBookings, TrekkerProfile
        │
        └── public/                      # Static branding assets and responsive background imagery
```

---

## 5. Pre-Seeded Default Accounts

When the application runs for the first time, it automatically initializes SQLite (`backend/tma_v2.db`) and seeds standard demonstration accounts with ready-to-test expeditions and bookings:

| Role | Email Address | Password | Permissions & Capabilities |
|:---|:---|:---|:---|
| **Administrator** | `admin@tma.com` | `admin123` | Full system control: user approval/blacklisting, expedition CRUD, staff assignment, reminders config, PDF/HTML reports |
| **Trek Staff (Approved)** | `aarav.staff@tma.com` | `staff123` | Active mountain guide: manages assigned treks, adjusts available slots, updates route status, views participant rosters |
| **Trek Staff (Pending)** | `vikram.staff@tma.com` | `staff123` | Registered staff applicant: login blocked until approved by Administrator |
| **Trekker (Customer)** | `rohan@example.com` | `trek123` | Registered user: browses open treks, books seats atomically, manages bookings, exports CSV history |

---

## 6. Installation & Execution Guide

### Prerequisites
- **Python:** Version 3.9, 3.10, 3.11, or 3.12
- **Redis Server:** Running locally on port `6379` (`brew install redis` or `sudo apt install redis-server`)
- **Node.js & npm (Optional):** Node.js 18+ (only needed if modifying frontend source code; the production build is already pre-compiled in `frontend/dist`)

---

### Option A: One-Click Startup (Recommended)

Run the included root startup script:

```bash
bash run.sh
```

This automated script will:
1. Detect or create a Python virtual environment (`.venv`) and install dependencies from `requirements.txt`.
2. Check and start the local **Redis** server if not already active.
3. Launch the **Celery Worker** in the background.
4. Launch the **Flask Server** on **`http://127.0.0.1:5001`**.

---

### Option B: Manual Step-by-Step Setup

#### 1. Start Redis
```bash
redis-server --daemonize yes
```
*(Verify Redis is active with `redis-cli ping` $\rightarrow$ returns `PONG`)*

#### 2. Setup Backend Python Environment
```bash
# From the project root
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. Start Celery Worker (in a separate terminal)
```bash
source .venv/bin/activate
cd backend
celery -A celery_worker worker --loglevel=info
```

*(Optional: To run Celery Beat periodic scheduler in another terminal)*
```bash
source .venv/bin/activate
cd backend
celery -A celery_worker beat --loglevel=info
```

#### 4. Start Flask Application
```bash
source .venv/bin/activate
cd backend
python3 run.py
```

The unified application (serving both the Flask REST API and compiled Vue 3 SPA) will be accessible at:  
👉 **`http://127.0.0.1:5001`**

---

### Option C: Frontend Development Mode (Hot-Reloading)

If you wish to edit and develop Vue components with Vite HMR:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server will open at **`http://localhost:5173`** and automatically proxy API calls (`/api/*`) to Flask on port `5001`.

To recompile the frontend for production:
```bash
cd frontend
npm run build
```
*(Compiled output is generated directly into `frontend/dist`, which Flask serves).*

---

## 7. Core Feature Highlights

### 7.1. Administrator Operations
- **Analytical Dashboard:** Live metrics displaying total registered trekkers, active guides, published expeditions, active reservations, and trail capacity charts (cached with Redis for 60 seconds).
- **User & Staff Management:**
  - Search and filter users by role and name (`?q=`).
  - Review and approve pending staff applicant accounts with a single click.
  - Deactivate/blacklist or reactivate accounts.
  - Delete users with safe cascade handling (booked slots are automatically restored to available trail capacity).
- **Expedition Route Management:** Create, edit, and delete trekking expeditions. Assign approved guides to routes.
- **Reporting Engine:** Generate monthly activity reports in HTML and downloadable vector **PDF** format (built with ReportLab).
- **Automated Reminder Controls:** Configure Celery reminder parameters (dispatch hour, lead days, webhook URL, SMTP credentials) and trigger immediate on-demand dispatches.

### 7.2. Trek Staff Operations
- **Guide Dashboard:** View metrics for assigned mountain expeditions, confirmed participants, and ongoing trek statuses.
- **Capacity & Slot Adjustments:** Update available seat capacity in real-time with an enforced validation floor (capacity cannot be lowered below already-confirmed bookings).
- **Status Workflow:** Transition treks through states: `Open` $\rightarrow$ `Closed` $\rightarrow$ `Started` $\rightarrow$ `Completed`. Marking a trek as `Completed` automatically marks all participant bookings as completed.
- **Participant Rosters:** View and download participant rosters with contact phone numbers and allocated seats.

### 7.3. Trekker Operations
- **Expedition Discovery:** Search available open treks by keyword (`?q=`), location, and filter by difficulty (`Easy`, `Moderate`, `Hard`).
- **Atomic Concurrency Booking:** Book seats with transactional guarantees preventing overbooking even under simultaneous multi-user checkout.
- **Reservation Ledger:** Track active and past expeditions with status badges (`Confirmed`, `Cancelled`, `Completed`).
- **One-Click Cancellation:** Cancel bookings anytime before expedition departure; restored seats immediately reflect in available trail capacity.
- **Asynchronous CSV Export:** Request an asynchronous Celery batch export of booking history. The file compiles in the background and is served for authenticated download.

---

## 8. Background Jobs & Caching Architecture

### 8.1. Celery Asynchronous & Scheduled Tasks
1. **Daily Upcoming Trek Reminders (`tasks.send_daily_reminders`):**
   - Scheduled via Celery Beat every day at 08:00 UTC.
   - Detects all treks departing within the configured lead window (1 to 5 days).
   - Generates personalized reminders with packing lists and safety advice.
   - Dispatches via Google Chat Webhook, Gmail SMTP, or local MIME file archive.
2. **Monthly Activity & Analytics Report (`tasks.generate_monthly_report`):**
   - Scheduled via Celery Beat on the 1st of every month at 00:00 UTC (`0 0 1 * *`).
   - Aggregates monthly expedition performance, revenues, and top-rated routes.
   - Generates high-fidelity vector PDF and HTML reports saved to `backend/exports/`.
3. **Asynchronous Booking History Export (`tasks.export_bookings_csv`):**
   - Offloads user CSV generation to background Celery workers to keep web request latency under 50ms.
   - Alerts the user upon task completion and provides a direct download link.

### 8.2. Redis Caching Strategy
- **Endpoints Cached:**
  - Admin Dashboard (`/api/v1/admin/dashboard`) $\rightarrow$ TTL 60 seconds
  - Trekker Route Catalog (`/api/v1/trekker/treks`) $\rightarrow$ TTL 300 seconds
- **Event-Driven Cache Invalidation:**
  - The cache is automatically purged when any expedition is created, updated, or deleted.
  - The cache is purged immediately when any booking is created or cancelled, ensuring trekkers always see accurate remaining seat counts.

---

## 9. Automated Testing Suite

The project includes **18 comprehensive automated integration test suites** written with `pytest`.

To run the complete test suite:

```bash
# From the project root
cd backend
pytest -v
```

### Test Coverage Highlights:
- **`test_auth.py`**: User registration, password hashing, JWT token issuance, role boundary protection, pending staff login lockout.
- **`test_booking_integrity.py`**: Transactional booking atomicity, concurrent reservation collisions on the last available seat, overbooking prevention, and cancellation seat recovery.
- **`test_admin_user_deletion.py`**: Safe deletion of users, cascading cancellations, and automatic slot replenishment.
- **`test_admin_pdf_reports.py`**: Verification of ReportLab monthly PDF report generation and HTML report rendering.
- **`test_celery_tasks.py`**: Celery asynchronous CSV export execution, file generation, and download integrity.
- **`test_notifications_and_email.py`**: Multi-channel reminder dispatching (Webhook, SMTP, MIME logger).
- **`test_reminders_and_schedule.py`**: Lead-window calculation and Celery Beat periodic schedule verification.

---

## 10. Academic Honesty & AI Declaration

I declare that this coursework submission represents my own work in accordance with the IIT Madras Code of Academic Integrity.

- **Student-Authored Core:** The database schemas, role-based authorization rules, transactional booking concurrency logic, Celery asynchronous pipelines, and Vue 3 reactive UI components were designed, authored, and verified by the student.
- **AI Tool Assistance:** Generative AI tools (Antigravity / Gemini) were utilized strictly as diagnostic auditors, PEP 8 / Vue linter advisors, and edge-case test case generators (e.g. concurrent race condition simulations).
- **Demonstration:** All features are demonstrable in a live environment in accordance with the submission guidelines.

**Student Name:** Hemant Singh Chauhan  
**Roll Number:** 24f2005964  
**Date:** November 2026
