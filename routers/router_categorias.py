from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Categoria
from schemas import CategoriaCreate, CategoriaUpdate, CategoriaRead

router = APIRouter(prefix="/categorias", tags=["Categorias"])

@router.get("/", response_model=List[CategoriaRead])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).all()

@router.get("/filtrar")
def filtrar_categorias(
    nombre: str = Query(..., description="cadena a buscar"),
    solo_codigos: bool = Query(True, description="si true, devuelve solo códigos"),
    db: Session = Depends(get_db),
):
    cats = db.query(Categoria).filter(Categoria.nombre.ilike(f"%{nombre}%")).all()
    if solo_codigos:
        return [{"codigo": c.codigo or str(c.id)} for c in cats]
    return [{"id": c.id, "codigo": c.codigo, "nombre": c.nombre} for c in cats]

@router.get("/by-codigo/{codigo}", response_model=CategoriaRead)
def categoria_por_codigo(codigo: str, db: Session = Depends(get_db)):
    cat = db.query(Categoria).filter(Categoria.codigo == codigo).first()
    if not cat: raise HTTPException(404, "Categoría no encontrada")
    return cat

@router.post("/", response_model=CategoriaRead, status_code=201)
def crear_categoria(data: CategoriaCreate, db: Session = Depends(get_db)):
    cat = Categoria(**data.model_dump())
    db.add(cat)
    try:
        db.commit(); db.refresh(cat)
        return cat
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Código de categoría duplicado")

@router.put("/{categoria_id}", response_model=CategoriaRead)
def actualizar_categoria(categoria_id: int, data: CategoriaUpdate, db: Session = Depends(get_db)):
    cat = db.get(Categoria, categoria_id)
    if not cat: raise HTTPException(404, "Categoría no encontrada")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    db.commit(); db.refresh(cat)
    return cat

@router.delete("/{categoria_id}", status_code=204)
def borrar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    cat = db.get(Categoria, categoria_id)
    if not cat: raise HTTPException(404, "Categoría no encontrada")
    db.delete(cat); db.commit()

