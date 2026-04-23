from fastapi import FastAPI
from .database import Base, engine
from .routes import incident, safety
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Incident + Safety System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incident.router)
app.include_router(safety.router)

@app.get("/health")
def health():
    return {"status": "ok"}