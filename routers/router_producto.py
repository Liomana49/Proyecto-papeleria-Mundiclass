# producto


productofrom fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud import crear_producto, listar_productos, obtener_producto, actualizar_producto, borrar_producto, productos_bajo_stock
from schemas import ProductoCreate, ProductoUpdate, ProductoRead

router = APIRouter()

@router.post("/", response_model=ProductoRead)
def create_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    return crear_producto(db, producto)

@router.get("/", response_model=list[ProductoRead])
def read_productos(db: Session = Depends(get_db)):
    return listar_productos(db)

@router.get("/{producto_id}", response_model=ProductoRead)
def read_producto(producto_id: int, db: Session = Depends(get_db)):
    return obtener_producto(db, producto_id)

@router.put("/{producto_id}", response_model=ProductoRead)
def update_producto(producto_id: int, producto: ProductoUpdate, db: Session = Depends(get_db)):
    return actualizar_producto(db, producto_id, producto)

@router.delete("/{producto_id}")
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    borrar_producto(db, producto_id)
    return {"message": "Producto deleted"}

@router.get("/bajo-stock", response_model=list[ProductoRead])
def read_productos_bajo_stock(db: Session = Depends(get_db)):
    return productos_bajo_stock(db)