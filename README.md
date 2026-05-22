# FamilyRoots

A private, full-stack family genealogy web application. Import from Ancestry.com via GEDCOM, manage people and relationships, and explore your family history through an interactive tree.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS |
| Tree visualization | React Flow |
| Backend | Python FastAPI |
| Database | PostgreSQL 16 |
| ORM / Migrations | SQLAlchemy 2 + Alembic |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Container | Docker Compose |

---

## Project Structure

```
FamilyRoots/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings from .env
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── routers/             # API route handlers
│   │   ├── services/
│   │   │   ├── gedcom_importer.py
│   │   │   ├── tree_service.py
│   │   │   ├── privacy_service.py
│   │   │   └── user_service.py
│   │   ├── auth/                # JWT + password hashing
│   │   └── utils/               # Logging, file validation
│   ├── alembic/                 # Database migrations
│   ├── create_admin.py          # One-time admin creation script
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Route definitions
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Full page views
│   │   ├── services/            # Axios API calls
│   │   ├── hooks/               # React hooks
│   │   ├── types/               # TypeScript interfaces
│   │   └── utils/               # Date helpers, privacy helpers
│   ├── package.json
│   └── .env.example
└── docker-compose.yml
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended)
- **Or** run locally:
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL 15+

---

## Quick Start — Docker Compose (Recommended)

```bash
# 1. Open the project folder
cd FamilyRoots

# 2. Build and start all services
docker compose up --build

# 3. Create your first admin user (in a new terminal)
docker compose exec backend python create_admin.py

# 4. Open the app
#    Frontend:  http://localhost
#    API docs:  http://localhost:8000/docs
```

---

## Local Development (No Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment file
copy .env.example .env
# Edit .env — set DATABASE_URL to your PostgreSQL connection

# Run migrations
alembic upgrade head

# Create first admin user
python create_admin.py

# Start API server
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

npm install
npm run dev
```

Frontend: `http://localhost:5173`

> The Vite dev server proxies all `/auth`, `/people`, `/tree`, etc. calls to `http://localhost:8000` automatically.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres:password@localhost:5432/familyroots` | PostgreSQL connection |
| `SECRET_KEY` | *(must change)* | JWT signing secret — use a long random string |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token lifetime |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |
| `UPLOAD_DIR` | `./uploads` | Local file upload directory |
| `MAX_GEDCOM_SIZE_MB` | `50` | GEDCOM upload size limit |

---

## Database Migrations

```bash
cd backend

# Apply all migrations
alembic upgrade head

# Create a new migration after changing models
alembic revision --autogenerate -m "description"

# Rollback one step
alembic downgrade -1
```

---

## Creating the First Admin User

```bash
# With Docker:
docker compose exec backend python create_admin.py

# Without Docker:
cd backend
python create_admin.py
```

---

## Importing a GEDCOM File

1. Log in as an Admin
2. Navigate to **Admin → Import GEDCOM**
3. Select your `.ged` file (exported from Ancestry.com or any genealogy software)
4. Click **Import GEDCOM**
5. Review the import summary

The importer handles GEDCOM 5.5.x. Duplicate people (matched by `external_id`) are skipped automatically.

---

## User Roles

| Role | Can do |
|---|---|
| **Admin** | Everything — manage users, import GEDCOM, edit/delete all records |
| **Editor** | Add and edit people and relationships |
| **Viewer** | Read-only; living people are hidden |

---

## API Reference

| Method | Path | Auth Required | Description |
|---|---|---|---|
| POST | `/auth/register` | None | Register |
| POST | `/auth/login` | None | Login → JWT |
| GET | `/auth/me` | User | Current user |
| GET | `/people` | User | List/search people |
| POST | `/people` | Editor | Create person |
| GET | `/people/{id}` | User | Person detail |
| PATCH | `/people/{id}` | Editor | Update person |
| DELETE | `/people/{id}` | Editor | Delete person |
| GET | `/people/{id}/relatives` | User | Family members |
| POST | `/relationships` | Editor | Create relationship |
| DELETE | `/relationships/{id}` | Editor | Delete relationship |
| GET | `/tree` | User | Tree nodes + edges |
| POST | `/gedcom/import` | Admin | Import GEDCOM |
| GET | `/admin/dashboard` | Admin | Site stats |
| GET/POST | `/admin/users` | Admin | Manage users |

Full interactive docs: `http://localhost:8000/docs`

---

## Privacy

Privacy logic lives in `backend/app/services/privacy_service.py` — one place to update if rules change.

- **Admin / Editor**: see all people including living
- **Viewer**: only sees people where `is_living = false`
- The GEDCOM importer marks anyone without a death date as `is_living = true`

---

## Current Limitations (V1 MVP)

- Tree uses a simple grid layout (upgrade path documented in `frontend/src/utils/treeLayout.ts`)
- No photo upload UI (API endpoint exists: `POST /media/person/{id}`)
- No inline relationship editor in person detail page
- No password reset or email invitations
- No GEDCOM export

---

## Future AWS Deployment

```
Route 53 → CloudFront → S3 (React build)
                   ↓
               ALB / API Gateway
                   ↓
         ECS Fargate / App Runner (FastAPI)
                   ↓
           RDS PostgreSQL (Multi-AZ)
                   ↓
           S3 (photos / documents)
```

Steps summary:
1. Push backend Docker image to ECR
2. Deploy on App Runner or ECS Fargate
3. Provision RDS PostgreSQL
4. Store `DATABASE_URL` and `SECRET_KEY` in AWS Secrets Manager / Parameter Store
5. Build frontend and sync to S3 (`npm run build && aws s3 sync dist/ s3://your-bucket`)
6. Create CloudFront distribution
7. Update backend CORS to include your CloudFront domain
