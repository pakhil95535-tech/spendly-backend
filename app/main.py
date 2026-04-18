from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, expenses, budget, ai
from app.models import user, expense  # Import models so tables are created

app = FastAPI(
    title="Spendly API",
    description="Rupee Expense Tracker Backend",
    version="1.0.0",
    contact={
        "name": "pakhil95535-tech",
        "url": "https://github.com/pakhil95535-tech",
    }
)

# Allow requests from Flutter app (any origin during development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(budget.router)
app.include_router(ai.router)

@app.on_event("startup")
async def startup():
    # Create all tables automatically on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")
@app.get("/")
async def root():
    return {"message": "Spendly API is running! Visit /docs for API documentation."}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Spendly API"}