from sqlalchemy.orm import Session
from hotel_map_broadcast_module.models.map_model import HotelMap
from hotel_map_broadcast_module.storage.file_handler import FileHandler
from fastapi import UploadFile

class MapService:
    @staticmethod
    def create_map(db: Session, file: UploadFile, description: str, floor: int, uploader: str):
        file_path = FileHandler.save_upload_file(file)
        new_map = HotelMap(
            image_path=file_path,
            description=description,
            floor_number=floor,
            uploaded_by=uploader
        )
        db.add(new_map)
        db.commit()
        db.refresh(new_map)
        return new_map

    @staticmethod
    def get_all_maps(db: Session):
        return db.query(HotelMap).all()

    @staticmethod
    def delete_map(db: Session, map_id: str):
        db_map = db.query(HotelMap).filter(HotelMap.id == map_id).first()
        if db_map:
            FileHandler.delete_file(db_map.image_path)
            db.delete(db_map)
            db.commit()
            return True
        return False

    @staticmethod
    def update_description(db: Session, map_id: str, description: str):
        db_map = db.query(HotelMap).filter(HotelMap.id == map_id).first()
        if db_map:
            db_map.description = description
            db.commit()
            db.refresh(db_map)
            return db_map
        return None
