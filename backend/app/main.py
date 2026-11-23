
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.volatility import router as volatility_router
from app.api.portfolio import router as portfolio_router

app = FastAPI(
    title="FINVEST IQ API",
    description="Financial Risk and Investment Intelligence Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio_router)
app.include_router(volatility_router)


@app.get("/")
def home():
    return {
        "message": "FINVEST IQ API is running",
        "status": "healthy",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "application": "FINVEST IQ",
        "version": "1.0.0",
    }
