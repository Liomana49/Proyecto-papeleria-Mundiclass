from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Producto, Categoria, HistorialEliminados
import schemas

router = APIRouter(prefix="/productos", tags=["Productos"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(tabla=tabla, registro_id=registro_id, descripcion=descripcion or "", fecha_eliminado=datetime.utcnow())
    db.add(h)

@router.get("/", response_model=List[schemas.ProductoRead])
async def listar_productos(
    nombre: Optional[str] = Query(None),
    min_stock: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Producto)
    if nombre: stmt = stmt.where(Producto.nombre.ilike(f"%{nombre}%"))
    if min_stock is not None: stmt = stmt.where(Producto.stock >= min_stock)
    res = await db.execute(stmt); return res.scalars().all()

@router.get("/{producto_id}", response_model=schemas.ProductoRead)
async def obtener_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Producto).where(Producto.id == producto_id))
    obj = res.scalar_one_or_none()
    if not obj: raise HTTPException(404, "Producto no encontrado")
    return obj

@router.get("/{producto_id}/precio")
async def precio_para_cantidad(producto_id: int, cantidad: int = 1, db: AsyncSession = Depends(get_db)):
    if cantidad <= 0: raise HTTPException(400, "Cantidad debe ser > 0")
    res = await db.execute(select(Producto).where(Producto.id == producto_id))
    p = res.scalar_one_or_none()
    if not p: raise HTTPException(404, "Producto no encontrado")
    precio = p.valor_unitario; umbral = p.umbral_mayor or 20
    if cantidad > umbral and p.valor_unitario_mayor is not None: precio = p.valor_unitario_mayor
    total = float(precio) * cantidad
    return {"producto_id": p.id, "nombre": p.nombre, "cantidad": cantidad,
            "umbral_mayor": umbral, "precio_unitario_aplicado": float(precio), "total": round(total, 2)}

@router.post("/", response_model=schemas.ProductoRead, status_code=status.HTTP_201_CREATED)
async def crear_producto(payload: schemas.ProductoCreate, db: AsyncSession = Depends(get_db)):
    if payload.categoria_id is not None:
        cat = await db.execute(select(Categoria).where(Categoria.id == payload.categoria_id))
        if not cat.scalar_one_or_none(): raise HTTPException(404, "Categoría no existe")
    obj = Producto(**payload.model_dump())
    db.add(obj); await db.commit(); await db.refresh(obj); return obj

@router.put("/{producto_id}", response_model=schemas.ProductoRead)
async def actualizar_producto(producto_id: int, payload: schemas.ProductoUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Producto).where(Producto.id == producto_id))
    obj = res.scalar_one_or_none()
    if not obj: raise HTTPException(404, "Producto no encontrado")
    data = payload.model_dump(exclude_none=True)
    if "categoria_id" in data and data["categoria_id"] is not None:
        cat = await db.execute(select(Categoria).where(Categoria.id == data["categoria_id"]))
        if not cat.scalar_one_or_none(): raise HTTPException(404, "Categoría no existe")
    for k, v in data.items(): setattr(obj, k, v)
    await db.commit(); await db.refresh(obj); return obj

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Producto).where(Producto.id == producto_id))
    obj = res.scalar_one_or_none()
    if not obj: raise HTTPException(404, "Producto no encontrado")
    await log_delete(db, "Producto", obj.id, f"Producto {obj.nombre} eliminado")
    await db.delete(obj); await db.commit()

@router.get("/historial/eliminados")
async def historial_productos_eliminados(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Producto")
        .order_by(HistorialEliminados.fecha_eliminado.desc())
    )
    return res.scalars().all()

