from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Usuario
from schemas import UsuarioCreate, UsuarioUpdate, UsuarioRead

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/", response_model=List[UsuarioRead])
def listar_usuarios(
    db: Session = Depends(get_db),
    tipo: Optional[str] = Query(None, description="mayorista | minorista"),
    cedula: Optional[str] = Query(None, description="coincidencia exacta"),
    frecuente: Optional[bool] = Query(None, description="cliente frecuente"),
    skip: int = 0, limit: int = 50
):
    q = db.query(Usuario)
    if tipo: q = q.filter(Usuario.tipo == tipo)
    if cedula: q = q.filter(Usuario.cedula == cedula)
    if frecuente is not None: q = q.filter(Usuario.cliente_frecuente == frecuente)
    return q.offset(skip).limit(limit).all()

@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    u = db.get(Usuario, usuario_id)
    if not u: raise HTTPException(404, "Usuario no encontrado")
    return u

@router.get("/by-cedula/{cedula}", response_model=UsuarioRead)
def obtener_por_cedula(cedula: str, db: Session = Depends(get_db)):
    u = db.query(Usuario).filter(Usuario.cedula == cedula).first()
    if not u: raise HTTPException(404, "Usuario no encontrado")
    return u

@router.post("/", response_model=UsuarioRead, status_code=201)
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    u = Usuario(**data.model_dump())
    db.add(u)
    try:
        db.commit(); db.refresh(u)
        return u
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Cédula ya registrada")

@router.put("/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(usuario_id: int, data: UsuarioUpdate, db: Session = Depends(get_db)):
    u = db.get(Usuario, usuario_id)
    if not u: raise HTTPException(404, "Usuario no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(u, k, v)
    db.commit(); db.refresh(u)
    return u

@router.delete("/{usuario_id}", status_code=204)
def borrar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    u = db.get(Usuario, usuario_id)
    if not u: raise HTTPException(404, "Usuario no encontrado")
    db.delete(u); db.commit()

