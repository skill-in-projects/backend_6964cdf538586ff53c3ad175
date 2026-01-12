import os
import sys
import asyncio
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to path for imports (where main.py is located)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Note: Models and Controllers are subdirectories of current_dir (root level),
# so they can be imported directly when current_dir is in sys.path

# Lifespan context manager to handle startup/shutdown gracefully
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events - startup and shutdown"""
    # Startup
    print("Starting Backend API...")
    try:
        yield
    except asyncio.CancelledError:
        # Gracefully handle cancellation during shutdown
        print("Application shutdown requested")
        raise
    finally:
        # Shutdown
        print("Shutting down Backend API...")

app = FastAPI(title="Backend API", version="1.0.0", lifespan=lifespan)

# CORS configuration - allow all origins for GitHub Pages deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (GitHub Pages uses *.github.io)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],  # Allow all headers (for CORS preflight)
)

# Try to import and register router
try:
    from Controllers.TestController import router as test_router
    app.include_router(test_router)
except Exception as e:
    print(f"Error importing TestController: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    # Create a dummy router for error reporting
    from fastapi import APIRouter
    test_router = APIRouter(prefix="/api/test", tags=["test"])
    @test_router.get("/")
    async def error_endpoint():
        return {
            "error": "Failed to load TestController",
            "details": str(e),
            "traceback": traceback.format_exc()
        }
    app.include_router(test_router)

@app.get("/")
async def root():
    return {
        "message": "Backend API is running",
        "status": "ok",
        "swagger": "/docs",
        "api": "/api/test"
    }

@app.get("/swagger")
async def swagger_redirect():
    """Redirect /swagger to /docs (FastAPI Swagger UI)"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health():
    """Health check endpoint that doesn't require database"""
    return {
        "status": "healthy",
        "service": "Backend API"
    }

if __name__ == "__main__":
    import uvicorn
    import asyncio
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on 0.0.0.0:{port}")
    # Use lifespan='on' to explicitly enable lifespan handling
    uvicorn.run(app, host="0.0.0.0", port=port, lifespan="on")
