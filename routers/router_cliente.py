from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.ClienteRead)
def create_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    return crud.crear_cliente(db, cliente)

@router.get("/", response_model=list[schemas.ClienteRead])
def read_clientes(db: Session = Depends(get_db)):
    return crud.listar_clientes(db)

@router.get("/{cliente_id}", response_model=schemas.ClienteRead)
def read_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return crud.obtener_cliente(db, cliente_id)

@router.put("/{cliente_id}", response_model=schemas.ClienteRead)
def update_cliente(cliente_id: int, cliente: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    return crud.actualizar_cliente(db, cliente_id, cliente)

@router.delete("/{cliente_id}")
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    crud.borrar_cliente(db, cliente_id)
    return {"message": "Cliente deleted"}
