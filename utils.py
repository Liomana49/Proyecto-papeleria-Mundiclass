import os
import uuid
from supabase import Client, create_client
from fastapi import UploadFile

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 👈 nombre EXACTO del bucket en Supabase
BUCKET_NAME = "Mundiclass"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def upload_image_to_supabase(file: UploadFile, folder: str = "categorias") -> str:
    """
    Sube una imagen a Supabase Storage (bucket Mundiclass) y devuelve la URL pública.
    'folder' es una carpeta lógica dentro del bucket.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL o Key no configuradas en variables de entorno")

    # extensión del archivo
    file_extension = (file.filename or "").split(".")[-1] or "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # ruta interna en el bucket, p.ej. "categorias/uuid.png"
    path_in_bucket = f"{folder}/{unique_filename}"

    file_content = await file.read()

    # 👉 SIEMPRE usamos el bucket Mundiclass
    # si el bucket no existiera, aquí saldría el 404
    supabase.storage.from_(BUCKET_NAME).upload(
        path_in_bucket,
        file_content,
    )

    # obtener URL pública
    public_url_response = supabase.storage.from_(BUCKET_NAME).get_public_url(path_in_bucket)
    public_url = public_url_response.get("publicUrl")
    if not public_url:
        raise RuntimeError("No se pudo obtener la URL pública después del upload")

    return public_url
