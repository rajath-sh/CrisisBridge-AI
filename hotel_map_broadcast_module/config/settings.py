import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODULE_NAME: str = "Hotel Map & Broadcast Module"
    DATABASE_URL: str = "sqlite:///./hotel_map_broadcast_module/hotel_map_broadcast.db"
    UPLOAD_DIR: str = "./hotel_map_broadcast_module/uploads/maps"
    
    # WebSocket settings
    WS_PATH: str = "/ws/broadcast"

    class Config:
        env_prefix = "MAP_BROADCAST_"

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
