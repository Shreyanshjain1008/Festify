<div align="center">

# ✦ FESTIFY

### One Campus. Countless Celebrations. One Platform.

**A campus fests and event management platform** that brings students, organizers, and administrators together to discover events, manage registrations, and make every fest easier to experience.

</div>

---

## Overview

Festify is a full-stack web application for managing college festivals and campus events. It provides separate experiences for **Students/Participants**, **Event Organizers**, and **Administrators**—from discovering the event lineup and registering for activities to managing events, reviewing applications, and monitoring festival activity.

The repository contains a Flask-based REST API backend with a PostgreSQL database powered by Supabase, along with a React-based frontend.
## Highlights

### For students
- Create an account and sign in.
- Explore the festival landing page and browse the **Events** lineup.
- Search and filter events by category.
- View event information and register for events.
- Track registrations in the student dashboard.
- Apply to become an organizer by submitting society details.
- Register for festival day passes and access QR-based passes.
- Submit event feedback and view submitted feedback.
- Use the FAQ/help experience for common questions.

### For organizers
- Manage an organizer profile.
- Create and edit events.
- Work with event categories such as Technical, Cultural, Music, Dance, Gaming, Sports, Literary, and Workshop.
- View organizer analytics and feedback associated with events.

### For administrators
- Access an administrative dashboard and overview analytics.
- Review organizer/society applications.
- Manage societies and venues.
- Review and manage users and events.
- View feedback and administrative analytics.

> Feature availability and permissions depend on the authenticated user's role and the backend API.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, Vite 8, JavaScript |
| Routing & UI | React Router, Lucide React, custom CSS |
| HTTP requests | Axios |
| Backend | Python, Flask 3 |
| API structure | Flask Blueprints, service and schema modules |
| Database | Supabase |
| Database migrations | Flask-Migrate / Alembic |
| Authentication | JWT, bcrypt |
| Additional utilities | OTP, QR-code generation, Pillow |
| Configuration | python-dotenv |
| Cross-origin requests | Flask-CORS |

## Repository Structure

```text
Festify/
├── FESTIFY-FRONTEND/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── Login.jsx
│   │   ├── Signup.jsx
│   │   ├── StudentDashboard.jsx
│   │   ├── OrganizerDashboard.jsx
│   │   ├── AdminDashboard.jsx
│   │   ├── UtkarshPage.jsx
│   │   └── *.css
│   ├── package.json
│   └── vite.config.js
│
└── FESTIFY-BACKEND/
    ├── app/
    │   ├── config/       # Application configuration
    │   ├── middleware/  # Authentication and role middleware
    │   ├── models/      # SQLAlchemy data models
    │   ├── routes/      # API blueprints / endpoints
    │   ├── schemas/     # Request and response schemas
    │   ├── services/    # Application/business logic
    │   └── utils/       # Email, OTP, password, QR and token utilities
    ├── .env.example
    ├── requirements.txt
    └── run.py
```

## Getting Started

Follow the steps below to run Festify locally. Open two terminals: one for the backend and one for the frontend.

### Prerequisites

Make sure the following are installed:

- **Python** (with `pip`)
- **npm**
- **Supabase** PostgreSQL database
- Git (optional, for cloning the repository)

### 1. Get the project

```bash
git clone <your-repository-url>
cd Festify
```

If you already have the project ZIP, extract it and open a terminal in the extracted `Festify` directory.

### 2. Configure and start the backend

Move into the backend directory:

```bash
cd FESTIFY-BACKEND
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file by copying `.env.example` to `.env`:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Update `.env` with your own configuration:

```env
# PostgreSQL / Supabase connection string
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_HOST:5432/postgres?sslmode=require

# Use strong, private values for application secrets
JWT_SECRET_KEY=replace-with-a-secure-jwt-secret
OTP_SECRET=replace-with-a-secure-otp-secret
OTP_EXPIRY_SECONDS=300

# Flask environment
FLASK_ENV=development

# Optional BREVO configuration for email delivery
BREVO_API_KEY = Your-Brevo-API-key
BREVO_SENDER_EMAIL = Festify-email
BREVO_SENDER_NAME = festify-name

# Optional public backend URL
PUBLIC_BASE_URL = backend-connection-url
```

Start the Flask application:

```bash
python run.py
```

The backend is configured to run on:

```text
http://127.0.0.1:5000
```

A basic health endpoint is available at `/`. The `/db-check` endpoint can be used to check database connectivity.

### 3. Configure and start the frontend

Open a second terminal and move into the frontend directory:

```bash
cd FESTIFY-FRONTEND
```

Install the dependencies:

```bash
npm install
```

Create a `.env` file in `FESTIFY-FRONTEND` and set the frontend API base URL:

```env
VITE_API_BASE_URL=http://127.0.0.1:5000
```

Run the Vite development server:

```bash
npm run dev
```

Open the local URL printed by Vite in your terminal (usually `http://localhost:5173`).

## Backend API Areas

The Flask application registers the following API blueprint prefixes:

| Prefix | Responsibility |
|---|---|
| `/api/auth` | Authentication |
| `/api/users` | User-related operations |
| `/api/societies` | Society management |
| `/api/organizers` | Organizer operations |
| `/api/venues` | Venue management |
| `/api/events` | Event operations |
| `/api/registrations` | Event registrations |
| `/api/day-passes` | Festival day-pass operations |
| `/api/pass` | Pass-related operations |
| `/api/feedback` | Feedback |
| `/api/analytics/organizer` | Organizer analytics |
| `/api/analytics/admin` | Admin analytics |
| `/api/faq` | FAQ/help content |
| `/api/admin` | Administrative operations |

The API is organized into route, schema, service, and model modules to keep request handling, validation, business logic, and database entities separated.

## Data Models

The backend includes models for key festival entities, including:

- Users
- Events and event reactions
- Event registrations
- Event custom fields and submitted custom values
- Societies and organizer profiles
- Venues
- Fest passes and day passes
- Feedback
- FAQ entries

## Notes for Developers

- The frontend reads its API base URL from `VITE_API_BASE_URL` and falls back to `http://127.0.0.1:5000`.
- The backend loads environment variables through `python-dotenv`.
- Configure a reachable PostgreSQL database before starting the backend.
- Configure SMTP credentials if you intend to use email delivery.
- JWT and OTP secrets should be unique, strong, and kept outside source control.
- Do not use the included development configuration as-is for production.
- The uploaded project archive contains local Python environment/dependency files. These are not required in source control; install dependencies from `requirements.txt` instead.

## Troubleshooting

**Frontend cannot reach the backend**
- Confirm the Flask server is running.
- Check `VITE_API_BASE_URL` in the frontend `.env` file.
- Restart the Vite server after changing environment variables.

**Database connection fails**
- Verify `DATABASE_URL`, database credentials, host, port, and network access.
- For Supabase/PostgreSQL, use the connection string and SSL settings supplied by your database provider.
- Visit `http://127.0.0.1:5000/db-check` to inspect database connectivity.

**Python imports or packages fail**
- Activate the backend virtual environment.
- Run `pip install -r requirements.txt` again.

**Frontend dependencies or scripts fail**
- Run `npm install` from `FESTIFY-FRONTEND`.
- Check that your installed Node.js version is compatible with the installed Vite version.

## Contributing

Contributions and improvements are welcome.

1. Create a branch for your change.
2. Keep frontend components and backend modules organized by responsibility.
3. Test the affected functionality locally.
4. Run `npm run lint` and `npm run build` for frontend changes.
5. Submit a pull request with a clear description of the change.

## License

No license file was present in the supplied project archive. Add a `LICENSE` file before distributing the project under an open-source license.

---

<div align="center">

**FESTIFY — Discover. Participate. Organize. Celebrate.**

</div>
