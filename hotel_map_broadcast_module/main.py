import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from hotel_map_broadcast_module.api.routes import router
from hotel_map_broadcast_module.db.repository import init_db

app = FastAPI(title="Hotel Map & Broadcast Module")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router)

@app.on_event("startup")
def on_startup():
    init_db()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
