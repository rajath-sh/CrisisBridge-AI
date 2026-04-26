import os
import shutil
from fastapi import UploadFile
from hotel_map_broadcast_module.config.settings import settings

class FileHandler:
    @staticmethod
    def save_upload_file(upload_file: UploadFile, folder: str = settings.UPLOAD_DIR) -> str:
        """Saves an uploaded file and returns its path."""
        file_path = os.path.join(folder, upload_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return file_path

    @staticmethod
    def delete_file(file_path: str):
        """Deletes a file from the filesystem."""
        if os.path.exists(file_path):
            os.remove(file_path)
