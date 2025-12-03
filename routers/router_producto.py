from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import schemas
import crud
from utils import upload_image_to_supabase

router = APIRouter(prefix="/api/productos", tags=["Productos"])

@router.get("/", response_model=List[schemas.ProductoRead])
async def listar_productos(
    nombre: Optional[str] = None,
    categoria_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud.listar_productos(db, nombre=nombre, min_stock=None)  # adapt as needed

@router.post("/", response_model=schemas.ProductoRead, status_code=status.HTTP_201_CREATED)
async def crear_producto(
    payload: schemas.ProductoCreate,
    imagen: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    # Si hay imagen, la subimos a Supabase y obtenemos la URL pública
    imagen_url: Optional[str] = None
    if imagen:
        if not imagen.content_type or not imagen.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser una imagen (jpg, png, etc.)",
            )
        # 👇 usamos folder="productos"
        imagen_url = await upload_image_to_supabase(imagen, folder="productos")

    # Si hay imagen_url, la agregamos al payload
    if imagen_url:
        payload.imagen_url = imagen_url

    return await crud.crear_producto(db, payload)

@router.put("/{producto_id}", response_model=schemas.ProductoRead)
async def actualizar_producto(
    producto_id: int,
    payload: schemas.ProductoUpdate,
    imagen: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    imagen_url: Optional[str] = None
    if imagen:
        if not imagen.content_type or not imagen.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser una imagen (jpg, png, etc.)",
            )
        # 👇 usamos folder="productos"
        imagen_url = await upload_image_to_supabase(imagen, folder="productos")

    # Si hay imagen_url, la agregamos al payload
    if imagen_url:
        payload.imagen_url = imagen_url

    return await crud.actualizar_producto(db, producto_id, payload)

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = await crud.obtener_producto(db, producto_id)

    descripcion = f"Producto '{producto.nombre}' eliminado"

    await crud._registrar_eliminado(db, "productos", producto.id, {"nombre": producto.nombre})
    await crud.borrar_producto(db, producto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/historial/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def historial_productos_eliminados(db: AsyncSession = Depends(get_db)):
    return await crud.listar_historial(db)


# ==========================
#   SUBIR IMAGEN PRODUCTO
# ==========================
@router.post("/{producto_id}/imagen")
async def subir_imagen_producto(
    producto_id: int,
    archivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    producto = await crud.obtener_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if not archivo.content_type or not archivo.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen (jpg, png, etc.)",
        )

    # 👇 usamos folder="productos"; bucket ya es 'Mundiclass'
    url_publica = await upload_image_to_supabase(archivo, folder="productos")

    # Guardar la imagen en la BD también desde este endpoint
    payload = schemas.ProductoUpdate(imagen_url=url_publica)
    await crud.actualizar_producto(db, producto_id, payload)

    return {
        "producto_id": producto_id,
        "url_publica": url_publica,
    }

