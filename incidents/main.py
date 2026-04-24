import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from database import Base, engine
from routes.incident import router as incident_router
from routes.safety import router as safety_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(incident_router)
app.include_router(safety_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(incident_router)
app.include_router(safety_router)

@app.get("/health")
def health():
    return {"status": "ok"}