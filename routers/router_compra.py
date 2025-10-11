from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud import crear_compra, listar_compras, obtener_compra, borrar_compra
from schemas import CompraCreate, CompraRead

router = APIRouter()

@router.post("/", response_model=CompraRead)
def create_compra(compra: CompraCreate, db: Session = Depends(get_db)):
    return crear_compra(db, compra)

@router.get("/", response_model=list[CompraRead])
def read_compras(db: Session = Depends(get_db)):
    return listar_compras(db)

@router.get("/{compra_id}", response_model=CompraRead)
def read_compra(compra_id: int, db: Session = Depends(get_db)):
    return obtener_compra(db, compra_id)

@router.delete("/{compra_id}")
def delete_compra(compra_id: int, db: Session = Depends(get_db)):
    borrar_compra(db, compra_id)
    return {"message": "Compra deleted"}
    