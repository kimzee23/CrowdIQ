from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

from src.shared.exceptions.base import CrowdIQException

from src.presentation.api.v1 import auth, predictions, users
from src.shared.configs.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions (e.g., connect to DB/Redis if needed at app level)
    yield
    # Shutdown actions

tags_metadata = [
    {
        "name": "Auth",
        "description": "Operations with users authentication. The **login** logic is also here.",
    },
    {
        "name": "Users",
        "description": "Operations with users. Retrieve profiles, follow/unfollow functionality.",
    },
    {
        "name": "Predictions",
        "description": "Manage predictions, categories, and voting operations.",
    },
    {
        "name": "Health",
        "description": "API health checks.",
    },
]

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="CrowdIQ API - Social prediction intelligence platform.",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")

@app.exception_handler(CrowdIQException)
async def crowdiq_exception_handler(request: Request, exc: CrowdIQException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to the Swagger UI documentation."""
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Health"])
async def health_check():
    """Check API health status."""
    return {"status": "healthy"}
