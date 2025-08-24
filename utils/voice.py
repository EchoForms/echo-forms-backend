from typing import Optional
from fastapi import UploadFile, File

async def extract_file_bytes(file: Optional[UploadFile] = File(None)) -> bytes:
    if not file:
        raise ValueError("No file provided")
    
    file_bytes = await file.read()
    
    if not file_bytes:
        raise ValueError("Empty file provided")
    
    # Reset file position for potential reuse
    await file.seek(0)
    
    return file_bytes