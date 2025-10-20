# routers/router_compra.py

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db  # alias a get_async_db
from models import Compra, Producto, Cliente
import schemas

router = APIRouter(prefix="/compras", tags=["Compras"])


# =========================================================
# LISTAR COMPRAS
# =========================================================
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
    if cliente_id:
        stmt = stmt.where(Compra.cliente_id == cliente_id)
    if producto_id:
        stmt = stmt.where(Compra.producto_id == producto_id)
    if desde:
        stmt = stmt.where(Compra.fecha >= desde)
    if hasta:
        stmt = stmt.where(Compra.fecha < hasta)
    res = await db.execute(stmt.limit(limit))
    return res.scalars().all()


# =========================================================
# OBTENER COMPRA POR ID
# =========================================================
@router.get("/{compra_id}", response_model=schemas.CompraRead)
async def obtener_compra(compra_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Compra).where(Compra.id == compra_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return obj


# =========================================================
# CALCULAR PRECIO PARA UNA CANTIDAD (SIN GUARDAR)
# =========================================================
@router.get("/precio/calcular")
async def calcular_precio(
    producto_id: int,
    cantidad: int = 1,
    db: AsyncSession = Depends(get_db),
):
    if cantidad <= 0:
        raise HTTPException(400, "Cantidad debe ser > 0")

    res = await db.execute(select(Producto).where(Producto.id == producto_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Producto no encontrado")

    precio_unit = p.valor_unitario
    umbral = p.umbral_mayor or 20
    if cantidad > umbral and p.valor_unitario_mayor is not None:
        precio_unit = p.valor_unitario_mayor

    total = float(precio_unit) * cantidad
    return {
        "producto_id": p.id,
        "nombre": p.nombre,
        "cantidad": cantidad,
        "umbral_mayor": umbral,
        "precio_unitario_aplicado": float(precio_unit),
        "total": round(total, 2),
    }


# =========================================================
# CREAR COMPRA (DESCUENTA STOCK)
# =========================================================
@router.post("/", response_model=schemas.CompraRead, status_code=status.HTTP_201_CREATED)
async def crear_compra(payload: schemas.CompraCreate, db: AsyncSession = Depends(get_db)):
    # valida cliente
    rcli = await db.execute(select(Cliente).where(Cliente.id == payload.cliente_id))
    cliente = rcli.scalar_one_or_none()
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")

    # valida producto
    rprod = await db.execute(select(Producto).where(Producto.id == payload.producto_id))
    producto = rprod.scalar_one_or_none()
    if not producto:
        raise HTTPException(404, "Producto no encontrado")

    if payload.cantidad <= 0:
        raise HTTPException(400, "La cantidad debe ser mayor a 0")

    if producto.stock < payload.cantidad:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Stock insuficiente")

    # descontar stock
    producto.stock -= payload.cantidad

    compra = Compra(
        cliente_id=payload.cliente_id,
        producto_id=payload.producto_id,
        cantidad=payload.cantidad,
        # fecha se setea por default en el modelo
    )

    db.add(producto)
    db.add(compra)
    await db.commit()
    await db.refresh(compra)
    return compra


# =========================================================
# ELIMINAR COMPRA
# =========================================================
@router.delete("/{compra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_compra(compra_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Compra).where(Compra.id == compra_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Compra no encontrada")
    await db.delete(obj)
    await db.commit()
