from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import insights_router

app = FastAPI(
    title="Agentic Insight Tracker",
    description="API for tracking and analyzing AI agent insights from blogs and changelogs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(insights_router)


@app.get("/")
async def root():
    return {"message": "Agentic Insight Tracker API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
