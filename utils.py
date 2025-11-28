import os
import uuid
from typing import Optional

from supabase import Client, create_client
from fastapi import UploadFile, HTTPException

SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")

# 👈 nombre EXACTO del bucket en Supabase (respetando may/min)
BUCKET_NAME = "Mundiclass"

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL o SUPABASE_KEY no están configuradas en las variables de entorno.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def upload_image_to_supabase(
    file: UploadFile,
    folder: str = "categorias",
) -> str:
    """
    Sube una imagen al bucket 'Mundiclass' de Supabase Storage y devuelve la URL pública.
    'folder' es una carpeta lógica dentro del bucket (por ejemplo: 'categorias').
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen (jpg, png, etc.)",
        )

    # extensión del archivo
    file_extension = (file.filename or "").split(".")[-1] or "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # ruta interna en el bucket, p.ej. "categorias/uuid.png"
    path_in_bucket = f"{folder}/{unique_filename}"

    # leer contenido del archivo
    file_content = await file.read()

    # subir a Storage en el bucket Mundiclass
    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            path_in_bucket,
            file_content,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error subiendo archivo a Supabase: {e}",
        )

    # obtener URL pública
    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(path_in_bucket)
    if not public_url:
        raise RuntimeError("No se pudo obtener la URL pública después del upload")

    return public_url
