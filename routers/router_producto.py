from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Producto, HistorialEliminados
import schemas

router = APIRouter(prefix="/productos", tags=["Productos"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos={"descripcion": descripcion or "", "timestamp": datetime.utcnow().isoformat()},
    )
    db.add(h)

@router.get("/", response_model=List[schemas.ProductoRead])
async def listar_productos(
    nombre: Optional[str] = Query(None),
    categoria_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Producto)
    conds = []
    if nombre:
        conds.append(Producto.nombre == nombre)
    if categoria_id is not None:
        conds.append(Producto.categoria_id == categoria_id)
    if conds:
        stmt = stmt.where(and_(*conds))
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/", response_model=schemas.ProductoRead, status_code=status.HTTP_201_CREATED)
async def crear_producto(payload: schemas.ProductoCreate, db: AsyncSession = Depends(get_db)):
    obj = Producto(**payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.put("/{producto_id}", response_model=schemas.ProductoRead)
async def actualizar_producto(producto_id: int, payload: schemas.ProductoUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Producto).where(Producto.id == producto_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Producto).where(Producto.id == producto_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    await log_delete(db, "Producto", obj.id, f"Producto '{obj.nombre}' eliminado")
    await db.delete(obj)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/historial/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def historial_productos_eliminados(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Producto")
        .order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()

