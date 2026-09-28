# 🌳 FamilyRoots

[![CI](https://github.com/robertogonzalez-dev/FamilyRoots/actions/workflows/ci.yml/badge.svg)](https://github.com/robertogonzalez-dev/FamilyRoots/actions/workflows/ci.yml)

**Build, explore and preserve your family history.** FamilyRoots is a full-stack web app for creating private family trees: add relatives, link parents and spouses, and explore generations of ancestors.

**Live demo:** _coming soon_ (frontend on Vercel, API on Render, Postgres on Neon)

## Features
- Account sign-up and login (Argon2 password hashing, JWT auth)
- Multiple private trees per user
- People with names, dates, places and notes
- Parent and spouse relationships, with integrity rules enforced by the API:
  - no one can be their own ancestor (cycle detection)
  - at most two parents per person
  - no self-links, duplicates or links across trees
- Generational tree view and an ancestors endpoint (N generations, breadth-first)

## Tech stack
| Layer | Tech |
|---|---|
| Frontend | React 19, TypeScript, Vite, React Router |
| API | FastAPI, SQLAlchemy 2, Pydantic v2, Alembic |
| Database | PostgreSQL 16 |
| Infra | Docker, docker-compose, GitHub Actions, Render, Vercel, Neon |

## Run locally

```bash
# 1. Postgres + API (applies migrations on start) -> http://localhost:8000/docs
docker compose up --build

# 2. Frontend -> http://localhost:5173
cd frontend && npm install && npm run dev
```

<details>
<summary>Without Docker</summary>

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate    # macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env                              # point DATABASE_URL at a Postgres
alembic upgrade head
uvicorn app.main:app --reload
```
</details>

## Tests

```bash
cd backend && pytest          # API tests on in-memory SQLite, ~99% coverage
cd frontend && npm run lint && npm run build
```

CI also runs the migrations against a real Postgres service and checks that the models and migrations are in sync (`alembic check`).

## API overview

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register`, `/auth/login` | Sign up and get a token |
| GET | `/auth/me` | Current user |
| GET/POST | `/trees` | List and create trees |
| GET/PUT/DELETE | `/trees/{id}` | Tree detail |
| GET | `/trees/{id}/graph` | All people and relationships (for rendering) |
| POST | `/trees/{id}/people` | Add a person |
| GET/PUT/DELETE | `/trees/{id}/people/{pid}` | Person detail |
| GET | `/trees/{id}/people/{pid}/ancestors?generations=4` | Ancestors, by generation |
| POST/DELETE | `/trees/{id}/relationships[/{rid}]` | Link and unlink people |

Interactive docs are at `/docs` when the API is running.

## Deploy
1. **Database:** create a free Neon Postgres and copy its connection string (use the `postgresql+psycopg://` scheme).
2. **API:** create a new Render Blueprint from this repo (`render.yaml`). Set `DATABASE_URL`, and set `CORS_ORIGINS` to your Vercel URL.
3. **Frontend:** import `frontend/` into Vercel and set `VITE_API_URL` to the Render URL.

## Roadmap
See [docs/SCOPE.md](docs/SCOPE.md). Next up: the live deployment, an interactive tree canvas, GEDCOM import and export, and shared trees.
