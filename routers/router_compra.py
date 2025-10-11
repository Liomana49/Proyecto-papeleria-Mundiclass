from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.CompraRead)
def create_compra(compra: schemas.CompraCreate, db: Session = Depends(get_db)):
    return crud.crear_compra(db, compra)

@router.get("/", response_model=list[schemas.CompraRead])
def read_compras(db: Session = Depends(get_db)):
    return crud.listar_compras(db)

@router.get("/{compra_id}", response_model=schemas.CompraRead)
def read_compra(compra_id: int, db: Session = Depends(get_db)):
    return crud.obtener_compra(db, compra_id)

@router.delete("/{compra_id}")
def delete_compra(compra_id: int, db: Session = Depends(get_db)):
    crud.borrar_compra(db, compra_id)
    return {"message": "Compra deleted"}
