from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud import crear_cliente, listar_clientes, obtener_cliente, actualizar_cliente, borrar_cliente
from schemas import ClienteCreate, ClienteUpdate, ClienteRead

router = APIRouter()

@router.post("/", response_model=ClienteRead)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    return crear_cliente(db, cliente)

@router.get("/", response_model=list[ClienteRead])
def read_clientes(db: Session = Depends(get_db)):
    return listar_clientes(db)

@router.get("/{cliente_id}", response_model=ClienteRead)
def read_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return obtener_cliente(db, cliente_id)

@router.put("/{cliente_id}", response_model=ClienteRead)
def update_cliente(cliente_id: int, cliente: ClienteUpdate, db: Session = Depends(get_db)):
    return actualizar_cliente(db, cliente_id, cliente)

@router.delete("/{cliente_id}")
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    borrar_cliente(db, cliente_id)
    return {"message": "Cliente deleted"}