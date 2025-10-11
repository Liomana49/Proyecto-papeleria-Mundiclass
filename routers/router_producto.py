from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.ProductoRead)
def create_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    return crud.crear_producto(db, producto)

@router.get("/", response_model=list[schemas.ProductoRead])
def read_productos(db: Session = Depends(get_db)):
    return crud.listar_productos(db)

@router.get("/{producto_id}", response_model=schemas.ProductoRead)
def read_producto(producto_id: int, db: Session = Depends(get_db)):
    return crud.obtener_producto(db, producto_id)

@router.put("/{producto_id}", response_model=schemas.ProductoRead)
def update_producto(producto_id: int, producto: schemas.ProductoUpdate, db: Session = Depends(get_db)):
    return crud.actualizar_producto(db, producto_id, producto)

@router.delete("/{producto_id}")
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    crud.borrar_producto(db, producto_id)
    return {"message": "Producto deleted"}

@router.get("/bajo-stock", response_model=list[schemas.ProductoRead])
def read_productos_bajo_stock(db: Session = Depends(get_db)):
    return crud.productos_bajo_stock(db)