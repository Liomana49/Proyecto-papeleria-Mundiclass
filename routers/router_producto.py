from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Producto
from schemas import ProductoCreate, ProductoUpdate, ProductoRead

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/", response_model=List[ProductoRead])
def listar_productos(
    db: Session = Depends(get_db),
    nombre: Optional[str] = Query(None, description="contiene"),
    min_stock: Optional[int] = Query(None, description="stock mínimo"),
    skip: int = 0, limit: int = 50
):
    q = db.query(Producto)
    if nombre: q = q.filter(Producto.nombre.ilike(f"%{nombre}%"))
    if min_stock is not None: q = q.filter(Producto.stock >= min_stock)
    return q.offset(skip).limit(limit).all()

@router.get("/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    p = db.get(Producto, producto_id)
    if not p: raise HTTPException(404, "Producto no encontrado")
    return p

@router.get("/{producto_id}/precio")
def precio_para_cantidad(producto_id: int, cantidad: int = 1, db: Session = Depends(get_db)):
    p = db.get(Producto, producto_id)
    if not p: raise HTTPException(404, "Producto no encontrado")
    if cantidad <= 0: raise HTTPException(400, "Cantidad debe ser > 0")

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
        "total": round(total, 2)
    }

@router.post("/", response_model=ProductoRead, status_code=201)
def crear_producto(data: ProductoCreate, db: Session = Depends(get_db)):
    p = Producto(**data.model_dump())
    db.add(p)
    try:
        db.commit(); db.refresh(p)
        return p
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Violación de unicidad en producto")

@router.put("/{producto_id}", response_model=ProductoRead)
def actualizar_producto(producto_id: int, data: ProductoUpdate, db: Session = Depends(get_db)):
    p = db.get(Producto, producto_id)
    if not p: raise HTTPException(404, "Producto no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit(); db.refresh(p)
    return p

@router.delete("/{producto_id}", status_code=204)
def borrar_producto(producto_id: int, db: Session = Depends(get_db)):
    p = db.get(Producto, producto_id)
    if not p: raise HTTPException(404, "Producto no encontrado")
    db.delete(p); db.commit()
