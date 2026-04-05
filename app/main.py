from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.database import Base, engine

# Create all tables on startup (use Alembic for production migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Dashboard API",
    description="""
## Finance Dashboard Backend

A role-based financial records management system.

### Roles
| Role     | Capabilities |
|----------|-------------|
| `viewer`   | View dashboard summary and records |
| `analyst`  | View + create/update/delete own records + access insights |
| `admin`    | Full access including user management |

### Quick Start
1. **Register** a user via `POST /api/auth/register`
2. **Login** via `POST /api/auth/login` to get a JWT token
3. Click **Authorize** above and enter: `Bearer <your_token>`
4. Use any endpoint based on your role
    """,
    version="1.0.0",
    contact={"name": "Finance API"},
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handlers ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler to prevent raw tracebacks leaking to the client."""
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal error occurred. Please try again."},
    )


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router)


@app.get("/", tags=["Health"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Finance Dashboard API is running"}
