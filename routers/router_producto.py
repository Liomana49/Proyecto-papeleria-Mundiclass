from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import schemas
import crud
from utils import upload_image_to_supabase

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/", response_model=List[schemas.ProductoRead])
async def listar_productos(
    nombre: Optional[str] = None,
    categoria_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud.listar_productos(db, nombre=nombre, min_stock=None)  # adapt as needed

@router.post("/", response_model=schemas.ProductoRead, status_code=status.HTTP_201_CREATED)
async def crear_producto(
    nombre: str = Query(...),
    descripcion: Optional[str] = Query(None),
    cantidad: int = Query(...),
    valor_unitario: float = Query(...),
    valor_mayorista: Optional[float] = Query(None),
    categoria_id: Optional[int] = Query(None),
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

    # Construimos el dict de datos para el schema
    data_dict = {
        "nombre": nombre,
        "cantidad": cantidad,
        "valor_unitario": valor_unitario,
    }
    if descripcion:
        data_dict["descripcion"] = descripcion
    if valor_mayorista is not None:
        data_dict["valor_mayorista"] = valor_mayorista
    if categoria_id is not None:
        data_dict["categoria_id"] = categoria_id
    if imagen_url:
        data_dict["imagen_url"] = imagen_url

    payload = schemas.ProductoCreate(**data_dict)
    return await crud.crear_producto(db, payload)

@router.put("/{producto_id}", response_model=schemas.ProductoRead)
async def actualizar_producto(
    producto_id: int,
    nombre: Optional[str] = Query(None),
    descripcion: Optional[str] = Query(None),
    cantidad: Optional[int] = Query(None),
    valor_unitario: Optional[float] = Query(None),
    valor_mayorista: Optional[float] = Query(None),
    categoria_id: Optional[int] = Query(None),
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

    payload = schemas.ProductoUpdate(
        nombre=nombre,
        descripcion=descripcion,
        cantidad=cantidad,
        valor_unitario=valor_unitario,
        valor_mayorista=valor_mayorista,
        categoria_id=categoria_id,
        imagen_url=imagen_url,
    )
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

