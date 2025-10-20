from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Compra, Producto, Cliente, HistorialEliminados
import schemas

router = APIRouter(prefix="/compras", tags=["Compras"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(tabla=tabla, registro_id=registro_id, descripcion=descripcion or "", fecha_eliminado=datetime.utcnow())
    db.add(h)

@router.get("/", response_model=List[schemas.CompraRead])
async def listar_compras(
    db: AsyncSession = Depends(get_db),
    cliente_id: Optional[int] = Query(None),
    producto_id: Optional[int] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    limit: int = 100,
):
    stmt = select(Compra).order_by(Compra.fecha.desc())
    if cliente_id: stmt = stmt.where(Compra.cliente_id == cliente_id)
    if producto_id: stmt = stmt.where(Compra.producto_id == producto_id)
    if desde: stmt = stmt.where(Compra.fecha >= desde)
    if hasta: stmt = stmt.where(Compra.fecha < hasta)
    res = await db.execute(stmt.limit(limit))
    return res.scalars().all()

@router.get("/{compra_id}", response_model=schemas.CompraRead)
async def obtener_compra(compra_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Compra).where(Compra.id == compra_id))
    obj = res.scalar_one_or_none()
    if not obj: raise HTTPException(404, "Compra no encontrada")
    return obj

@router.post("/", response_model=schemas.CompraRead, status_code=status.HTTP_201_CREATED)
async def crear_compra(payload: schemas.CompraCreate, db: AsyncSession = Depends(get_db)):
    cli = await db.execute(select(Cliente).where(Cliente.id == payload.cliente_id))
    if not cli.scalar_one_or_none(): raise HTTPException(404, "Cliente no encontrado")
    pr = await db.execute(select(Producto).where(Producto.id == payload.producto_id))
    prod = pr.scalar_one_or_none()
    if not prod: raise HTTPException(404, "Producto no encontrado")
    if payload.cantidad <= 0: raise HTTPException(400, "La cantidad debe ser mayor a 0")
    if prod.stock < payload.cantidad: raise HTTPException(status.HTTP_400_BAD_REQUEST, "Stock insuficiente")
    prod.stock -= payload.cantidad
    compra = Compra(cliente_id=payload.cliente_id, producto_id=payload.producto_id, cantidad=payload.cantidad)
    db.add(prod); db.add(compra); await db.commit(); await db.refresh(compra); return compra

@router.delete("/{compra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_compra(compra_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Compra).where(Compra.id == compra_id))
    obj = res.scalar_one_or_none()
    if not obj: raise HTTPException(404, "Compra no encontrada")
    await log_delete(db, "Compra", obj.id, f"Compra eliminada (cliente_id={obj.cliente_id}, producto_id={obj.producto_id})")
    await db.delete(obj); await db.commit()

@router.get("/historial/eliminados")
async def historial_compras_eliminadas(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Compra")
        .order_by(HistorialEliminados.fecha_eliminado.desc())
    )
    return res.scalars().all()
