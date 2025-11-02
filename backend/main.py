import sys
from pathlib import Path

# Add parent directory to path so backend module can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from backend.routes import auth_routes, event_routes, attendance_routes, admin_routes, enrollment_routes
from fastapi.middleware.cors import CORSMiddleware
from backend.database.connection import client

app = FastAPI(title="Location-Based Attendance System", version="1.0.0")

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, tags=["Authentication"])
app.include_router(event_routes.router, tags=["Events"])
app.include_router(attendance_routes.router, tags=["Attendance"])
app.include_router(admin_routes.router, tags=["Admin"])
app.include_router(enrollment_routes.router, tags=["Enrollments"])

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    try:
        # Test database connection
        await client.admin.command('ping')
        print("\n" + "="*60)
        print("✅ DATABASE CONNECTION SUCCESSFUL")
        print("="*60)
        print("📊 Location-Based Attendance System is Ready!")
        print("📍 Backend running on: http://localhost:8001")
        print("📖 API Documentation: http://localhost:8001/docs")
        print("="*60 + "\n")
    except Exception as e:
        print("\n" + "="*60)
        print("❌ DATABASE CONNECTION FAILED")
        print("="*60)
        print(f"Error: {str(e)}")
        print("⚠️  Make sure MongoDB is running and accessible")
        print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    client.close()
    print("\n✋ Database connection closed")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Location-Based Attendance System",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Check if the service and database are healthy"""
    try:
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "service": "running"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "service": "running",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
