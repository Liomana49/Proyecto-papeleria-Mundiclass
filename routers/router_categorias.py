from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud import crear_categoria, listar_categorias, obtener_categoria, actualizar_categoria, borrar_categoria
from schemas import CategoriaCreate, CategoriaUpdate, CategoriaRead

router = APIRouter()

@router.post("/", response_model=CategoriaRead)
def create_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    return crear_categoria(db, categoria)

@router.get("/", response_model=list[CategoriaRead])
def read_categorias(db: Session = Depends(get_db)):
    return listar_categorias(db)

@router.get("/{categoria_id}", response_model=CategoriaRead)
def read_categoria(categoria_id: int, db: Session = Depends(get_db)):
    return obtener_categoria(db, categoria_id)

@router.put("/{categoria_id}", response_model=CategoriaRead)
def update_categoria(categoria_id: int, categoria: CategoriaUpdate, db: Session = Depends(get_db)):
    return actualizar_categoria(db, categoria_id, categoria)

@router.delete("/{categoria_id}")
def delete_categoria(categoria_id: int, db: Session = Depends(get_db)):
    borrar_categoria(db, categoria_id)
    return {"message": "Categoria deleted"}