import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import auth, people, relationships, tree, gedcom, admin, media, sources
from app.utils.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FamilyRoots API",
    description="Private family genealogy platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(people.router, prefix="/people", tags=["people"])
app.include_router(relationships.router, prefix="/relationships", tags=["relationships"])
app.include_router(tree.router, prefix="/tree", tags=["tree"])
app.include_router(gedcom.router, prefix="/gedcom", tags=["gedcom"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(media.router, prefix="/media", tags=["media"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "version": "1.0.0"}
