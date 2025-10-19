from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Cliente, Usuario
from schemas import ClienteCreate, ClienteUpdate, ClienteRead

router = APIRouter(prefix="/clientes", tags=["Clientes"])


# =========================================================
# LISTAR CLIENTES (con filtros)
# =========================================================
@router.get("/", response_model=List[ClienteRead])
def listar_clientes(
    db: Session = Depends(get_db),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre de usuario asociado"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de usuario (mayorista o minorista)"),
    frecuente: Optional[bool] = Query(None, description="Filtrar si el usuario es cliente frecuente"),
    skip: int = 0,
    limit: int = 50
):
    """
    Lista todos los clientes con filtros opcionales:
    - nombre: busca coincidencias parciales en el nombre del usuario.
    - activo: True/False.
    - tipo: 'mayorista' o 'minorista' (desde el Usuario).
    - frecuente: si el usuario tiene cliente_frecuente = True.
    """
    q = db.query(Cliente).join(Usuario)

    if nombre:
        q = q.filter(Usuario.nombre.ilike(f"%{nombre}%"))
    if tipo:
        q = q.filter(Usuario.tipo == tipo)
    if frecuente is not None:
        q = q.filter(Usuario.cliente_frecuente == frecuente)
    if activo is not None:
        q = q.filter(Cliente.activo == activo)

    return q.offset(skip).limit(limit).all()


# =========================================================
# OBTENER CLIENTE POR ID
# =========================================================
@router.get("/{cliente_id}", response_model=ClienteRead)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


# =========================================================
# OBTENER CLIENTE POR CÉDULA (desde su usuario)
# =========================================================
@router.get("/by-cedula/{cedula}", response_model=ClienteRead)
def cliente_por_cedula(cedula: str, db: Session = Depends(get_db)):
    """
    Retorna el cliente a partir de la cédula del usuario asociado.
    """
    cliente = (
        db.query(Cliente)
        .join(Usuario)
        .filter(Usuario.cedula == cedula)
        .first()
    )
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado con esa cédula")
    return cliente


# =========================================================
# CREAR CLIENTE
# =========================================================
@router.post("/", response_model=ClienteRead, status_code=201)
def crear_cliente(data: ClienteCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo cliente enlazado a un Usuario existente.
    """
    usuario = db.get(Usuario, data.usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no existe")

    # verificar si ya tiene cliente
    if db.query(Cliente).filter(Cliente.usuario_id == data.usuario_id).first():
        raise HTTPException(status_code=400, detail="Este usuario ya tiene un perfil de cliente")

    cliente = Cliente(**data.model_dump())
    db.add(cliente)
    try:
        db.commit()
        db.refresh(cliente)
        return cliente
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear el cliente")


# =========================================================
# ACTUALIZAR CLIENTE
# =========================================================
@router.put("/{cliente_id}", response_model=ClienteRead)
def actualizar_cliente(cliente_id: int, data: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(cliente, k, v)

    db.commit()
    db.refresh(cliente)
    return cliente


# =========================================================
# ELIMINAR CLIENTE
# =========================================================
@router.delete("/{cliente_id}", status_code=204)
def borrar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(cliente)
    db.commit()

