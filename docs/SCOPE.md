# FamilyRoots: scope and milestones

## Goal
A **live, deployed** full-stack app that someone can sign up for and use. It shows auth, relational data modeling of a graph (people and relationships) with integrity rules, a typed API, a React/TypeScript frontend, migrations, CI and cloud deployment. Scope is roughly 4 to 6 weekends.

## Architecture
- **Frontend:** React 19 + TypeScript + Vite, deployed on **Vercel** (free).
- **API:** FastAPI + SQLAlchemy 2 + Alembic, containerized, deployed on **Render** (free web service).
- **Database:** Postgres on **Neon** (free tier, doesn't expire).
- **Auth:** email and password (Argon2 hashing), JWT bearer tokens.

## MVP (done in the scaffold)
- [x] Register, log in, `/auth/me`
- [x] Trees: CRUD, private per user (404 on other users' trees)
- [x] People: CRUD
- [x] Relationships: parent and spouse, with no self-links, no cycles, max 2 parents, no cross-tree links, no duplicates
- [x] Graph endpoint plus an ancestors endpoint (breadth-first, N generations)
- [x] Frontend: login/register, tree list, generational tree view, add-person and link forms
- [x] Alembic migrations, Docker, docker-compose, CI (Postgres service), Render and Vercel configs

## Milestones to "portfolio-ready"
1. **Deploy (weekend 1).** Set up Neon, Render and Vercel, put the live URL in the README, and seed a demo account and tree.
2. **Better tree visualization (weekend 2).** Use React Flow or d3-hierarchy with pan and zoom, draw parent and spouse edges, and open a person detail drawer on click.
3. **GEDCOM import and export (weekend 3).** Import and export the standard genealogy file format. This is a strong "real-world data parsing" talking point. Write tests with sample GEDCOM files.
4. **Collaboration (weekend 4).** Invite a relative by email with a viewer or editor role (a `tree_members` table replacing `owner_id` checks).
5. **Polish (weekend 5).** Photo uploads (S3 or Cloudflare R2 presigned URLs), full-text search on names, Playwright end-to-end tests in CI, and a Lighthouse pass.

## Stretch goals
- Relationship calculator ("how is X related to Y?"), the lowest-common-ancestor problem
- Timeline view of births, deaths and places on a map
- Refresh tokens and password reset over email
