from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import get_db
from models import Compra, DetalleCompra, Producto, Cliente
from schemas import CompraCreate, CompraRead

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.get("/", response_model=List[CompraRead])
def listar_compras(
    db: Session = Depends(get_db),
    cliente_id: Optional[int] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    skip: int = 0, limit: int = 50
):
    q = db.query(Compra)
    if cliente_id: q = q.filter(Compra.cliente_id == cliente_id)
    if desde: q = q.filter(Compra.creado_en >= desde)
    if hasta: q = q.filter(Compra.creado_en < hasta)
    return q.offset(skip).limit(limit).all()

@router.get("/{compra_id}", response_model=CompraRead)
def obtener_compra(compra_id: int, db: Session = Depends(get_db)):
    c = db.get(Compra, compra_id)
    if not c: raise HTTPException(404, "Compra no encontrada")
    return c

@router.post("/", response_model=CompraRead, status_code=201)
def crear_compra(payload: CompraCreate, db: Session = Depends(get_db)):
    # valida cliente
    if not db.get(Cliente, payload.cliente_id):
        raise HTTPException(404, "Cliente no existe")

    compra = Compra(cliente_id=payload.cliente_id, subtotal=0, total=0)
    db.add(compra); db.flush()  # para tener compra.id

    subtotal = 0
    for item in payload.items:
        prod = db.get(Producto, item.producto_id)
        if not prod:
            raise HTTPException(404, f"Producto {item.producto_id} no existe")

        # precio según regla (> umbral usa valor_unitario_mayor si existe)
        precio_unit = prod.valor_unitario
        umbral = prod.umbral_mayor or 20
        if item.cantidad > umbral and prod.valor_unitario_mayor is not None:
            precio_unit = prod.valor_unitario_mayor

        # si el cliente envía manualmente un precio, lo ignoramos y usamos el calculado
        precio_aplicado = precio_unit

        # (opcional) controlar stock
        if prod.stock is not None and prod.stock < item.cantidad:
            raise HTTPException(400, f"Stock insuficiente para {prod.nombre}")
        # prod.stock -= item.cantidad  # si deseas descontar stock
        # db.add(prod)

        det = DetalleCompra(
            compra_id=compra.id,
            producto_id=prod.id,
            cantidad=item.cantidad,
            precio_unitario_aplicado=precio_aplicado
        )
        db.add(det)
        subtotal += float(precio_aplicado) * item.cantidad

    compra.subtotal = subtotal
    compra.total = subtotal  # impuestos/descuentos si aplica
    db.commit(); db.refresh(compra)
    return compra
