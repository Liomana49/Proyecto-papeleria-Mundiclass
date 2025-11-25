from typing import List, Optional
import os
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    Response,
    UploadFile,
    File,
)
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import schemas
import crud

router = APIRouter(prefix="/categorias", tags=["Categorias"])

@router.get("/", response_model=List[schemas.CategoriaRead])
async def listar_categorias(
    nombre: Optional[str] = None,
    codigo: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud.listar_categorias(db)

@router.post(
    "/",
    response_model=schemas.CategoriaRead,
    status_code=status.HTTP_201_CREATED,
)
async def crear_categoria(
    payload: schemas.CategoriaCreate,
    db: AsyncSession = Depends(get_db),
):
    return await crud.crear_categoria(db, payload)

@router.put("/{categoria_id}", response_model=schemas.CategoriaRead)
async def actualizar_categoria(
    categoria_id: int,
    payload: schemas.CategoriaUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await crud.actualizar_categoria(db, categoria_id, payload)

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_db),
):
    categoria = await crud.obtener_categoria(db, categoria_id)

    descripcion = f"Categoría '{categoria.nombre}' eliminada"

    await crud._registrar_eliminado(db, "categorias", categoria.id, {"nombre": categoria.nombre})
    await crud.borrar_categoria(db, categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get(
    "/historial/eliminados",
    response_model=List[schemas.HistorialEliminadoRead],
)
async def historial_categorias_eliminadas(
    db: AsyncSession = Depends(get_db),
):
    return await crud.listar_historial(db)

# ==========================
#   SUBIR IMAGEN CATEGORÍA
# ==========================
@router.post("/{categoria_id}/imagen")
async def subir_imagen_categoria(
    categoria_id: int,
    archivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    categoria = await crud.obtener_categoria(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if not archivo.content_type or not archivo.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen (jpg, png, etc.)",
        )

    carpeta = "static/categorias"
    os.makedirs(carpeta, exist_ok=True)

    extension = os.path.splitext(archivo.filename or "")[1] or ".jpg"
    nombre_archivo = f"cat_{categoria_id}_{uuid4().hex}{extension}"
    ruta_fisica = os.path.join(carpeta, nombre_archivo)

    contenido = await archivo.read()
    with open(ruta_fisica, "wb") as f:
        f.write(contenido)

    url_publica = f"/static/categorias/{nombre_archivo}"

    # Optionally, update categoria with imagen_url here if schema/model supports it
    # categoria.imagen_url = url_publica
    # await db.commit()
    # await db.refresh(categoria)

    return {
        "categoria_id": categoria_id,
        "filename": nombre_archivo,
        "imagen_url": url_publica,
    }

