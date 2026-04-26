from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from hotel_map_broadcast_module.db.repository import get_db
from hotel_map_broadcast_module.service.map_service import MapService
from hotel_map_broadcast_module.service.broadcast_service import BroadcastService
from hotel_map_broadcast_module.schemas.map_schema import MapResponse
from hotel_map_broadcast_module.schemas.broadcast_schema import BroadcastCreate, BroadcastResponse
from hotel_map_broadcast_module.schemas.location_schema import LocationCreate, LocationResponse
from hotel_map_broadcast_module.realtime.broadcast_ws import manager

from shared.dependencies import get_current_user, require_role
from shared.enums import UserRole
from shared.models import User
from hotel_map_broadcast_module.models.map_model import HotelLocation

router = APIRouter()

# --- MAP APIs ---

@router.post("/maps/upload", response_model=MapResponse)
async def upload_map(
    file: UploadFile = File(...),
    description: str = Form(None),
    floor_number: int = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    return MapService.create_map(db, file, description, floor_number, current_user.username)

@router.get("/maps", response_model=List[MapResponse])
async def get_maps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return MapService.get_all_maps(db)

@router.get("/maps/image/{map_id}")
async def get_map_image(
    map_id: str,
    db: Session = Depends(get_db)
):
    from hotel_map_broadcast_module.models.map_model import HotelMap
    db_map = db.query(HotelMap).filter(HotelMap.id == map_id).first()
    if not db_map:
        raise HTTPException(status_code=404, detail="Map record not found")
    
    # Normalize path for the current OS
    clean_path = os.path.normpath(db_map.image_path)
    if not os.path.exists(clean_path):
        # Try fallback: check if file exists just by filename in the upload dir
        filename = os.path.basename(clean_path)
        from hotel_map_broadcast_module.config.settings import settings
        fallback_path = os.path.join(settings.UPLOAD_DIR, filename)
        if os.path.exists(fallback_path):
            return FileResponse(fallback_path)
        raise HTTPException(status_code=404, detail=f"Image file not found at {clean_path}")
        
    return FileResponse(clean_path)

# --- LOCATION APIs ---

@router.post("/locations", response_model=LocationResponse)
async def create_location(
    loc_in: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    new_loc = HotelLocation(name=loc_in.name, floor=loc_in.floor)
    db.add(new_loc)
    try:
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Location already exists")
    db.refresh(new_loc)
    return new_loc

@router.get("/locations", response_model=List[LocationResponse])
async def get_locations(
    db: Session = Depends(get_db)
):
    """Public endpoint — locations are reference data for incident reporting."""
    return db.query(HotelLocation).all()

@router.delete("/locations/{loc_id}")
async def delete_location(
    loc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    loc = db.query(HotelLocation).filter(HotelLocation.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(loc)
    db.commit()
    return {"status": "Location deleted"}

@router.put("/locations/{loc_id}", response_model=LocationResponse)
async def update_location(
    loc_id: str,
    loc_in: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    loc = db.query(HotelLocation).filter(HotelLocation.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    
    loc.name = loc_in.name
    loc.floor = loc_in.floor
    
    try:
        db.commit()
        db.refresh(loc)
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Update failed")
        
    return loc

@router.delete("/maps/{map_id}")
async def delete_map(
    map_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    if not MapService.delete_map(db, map_id):
        raise HTTPException(status_code=404, detail="Map not found")
    return {"status": "Map deleted"}

@router.put("/maps/{map_id}", response_model=MapResponse)
async def update_map_description(
    map_id: str, 
    description: str = Form(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    updated_map = MapService.update_description(db, map_id, description)
    if not updated_map:
        raise HTTPException(status_code=404, detail="Map not found")
    return updated_map

# --- BROADCAST APIs ---

@router.post("/broadcast", response_model=BroadcastResponse)
async def create_broadcast(
    broadcast_in: BroadcastCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    return await BroadcastService.create_broadcast(db, broadcast_in, current_user.username)

@router.get("/broadcast", response_model=List[BroadcastResponse])
async def get_broadcasts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return BroadcastService.get_all_broadcasts(db)

@router.delete("/broadcast/{broadcast_id}")
async def delete_broadcast(
    broadcast_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    if not BroadcastService.delete_broadcast(db, broadcast_id):
        raise HTTPException(status_code=404, detail="Broadcast not found")
    return {"status": "Broadcast deleted"}

# --- WEBSOCKET ---

@router.websocket("/ws/broadcast")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
