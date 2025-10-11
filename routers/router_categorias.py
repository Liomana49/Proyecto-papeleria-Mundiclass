from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.CategoriaRead)
def create_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    return crud.crear_categoria(db, categoria)

@router.get("/", response_model=list[schemas.CategoriaRead])
def read_categorias(db: Session = Depends(get_db)):
    return crud.listar_categorias(db)

@router.get("/{categoria_id}", response_model=schemas.CategoriaRead)
def read_categoria(categoria_id: int, db: Session = Depends(get_db)):
    return crud.obtener_categoria(db, categoria_id)

@router.put("/{categoria_id}", response_model=schemas.CategoriaRead)
def update_categoria(categoria_id: int, categoria: schemas.CategoriaUpdate, db: Session = Depends(get_db)):
    return crud.actualizar_categoria(db, categoria_id, categoria)

@router.delete("/{categoria_id}")
def delete_categoria(categoria_id: int, db: Session = Depends(get_db)):
    crud.borrar_categoria(db, categoria_id)
    return {"message": "Categoria deleted"}
