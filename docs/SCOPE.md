# FamilyRoots: roadmap to portfolio-ready

FamilyRoots is a private family genealogy site: import an Ancestry.com GEDCOM, manage people and relationships, and explore the family through an interactive tree. Living relatives are kept private from viewers.

## Done
- [x] FastAPI + SQLAlchemy 2 + Alembic backend: people, relationships, events, sources, media, admin, GEDCOM import
- [x] React + TypeScript + Tailwind frontend with an interactive React Flow tree
- [x] Roles (admin / editor / viewer) and living-person privacy, enforced across every endpoint
- [x] Relationship integrity rules (no cycles, at most 2 biological parents, no duplicates)
- [x] Maintained auth stack (PyJWT + Argon2), with legacy bcrypt hashes upgraded on login
- [x] 23 backend tests, Ruff, ESLint, and CI with Postgres migration checks
- [x] Docker Compose for local use; Render + Vercel + Neon configs for free hosting

## Next milestones
1. **Go live.** Deploy on Render, Vercel and Neon, import a sanitized demo GEDCOM, and add a read-only demo viewer account and the live URL to the README.
2. **Durable uploads.** Store photos in S3 or Cloudflare R2 (presigned uploads) instead of the local disk, and add a photo upload UI on the person page.
3. **Better tree layout.** Replace the grid layout with dagre generations (the dependency is already installed) and focus the view on a selected person.
4. **GEDCOM export** so the data isn't locked in; round-trip tests (import, then export, then import).
5. **Invitations and password reset** by email, so relatives can join as viewers without self-registration.
6. **End-to-end tests** with Playwright in CI: log in, import, and open the tree.

## Stretch goals
- Relationship calculator ("how is X related to Y?")
- Timeline and map views of births, deaths and places
- Duplicate-person detection across multiple GEDCOM imports
