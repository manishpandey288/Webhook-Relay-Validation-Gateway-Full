from fastapi import FastAPI
import uvicorn
import asyncio
from contextlib import asynccontextmanager
from routes import webhook_routes, admin_routes
from db.database import init_db
from workers.event_worker import worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    asyncio.create_task(worker.worker_loop())
    yield
    # Shutdown
    worker.stop()

app = FastAPI(title="Webhook Gateway Validation System", lifespan=lifespan)

# Include routers first
app.include_router(webhook_routes.router, tags=["webhook"])
app.include_router(admin_routes.router, prefix="/admin", tags=["admin"])

# Root endpoint - defined after routers to ensure it's registered
@app.get("/", include_in_schema=True)
async def read_root():
    return {
        "message": "Webhook Gateway Validation System",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

