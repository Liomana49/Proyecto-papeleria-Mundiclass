from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Categoria
from producto import Producto
from cliente import Cliente
from compra import Compra
from usuario import Usuario
import schemas

# --------- Categorías ---------
def crear_categoria(db: Session, data: schemas.CategoriaCreate) -> Categoria:
    if db.query(Categoria).filter(Categoria.nombre == data.nombre).first():
        raise HTTPException(400, "La categoría ya existe")
    obj = Categoria(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def listar_categorias(db: Session) -> List[Categoria]:
    return db.query(Categoria).all()

def obtener_categoria(db: Session, categoria_id: int) -> Categoria:
    obj = db.query(Categoria).get(categoria_id)
    if not obj: raise HTTPException(404, "Categoría no encontrada")
    return obj

def actualizar_categoria(db: Session, categoria_id: int, data: schemas.CategoriaUpdate) -> Categoria:
    obj = obtener_categoria(db, categoria_id)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

def borrar_categoria(db: Session, categoria_id: int) -> None:
    obj = obtener_categoria(db, categoria_id)
    db.delete(obj); db.commit()

# --------- Productos ---------
def crear_producto(db: Session, data: schemas.ProductoCreate) -> Producto:
    _ = obtener_categoria(db, data.categoria_id)  # valida FK
    obj = Producto(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def listar_productos(db: Session) -> List[Producto]:
    return db.query(Producto).all()

def obtener_producto(db: Session, producto_id: int) -> Producto:
    obj = db.query(Producto).get(producto_id)
    if not obj: raise HTTPException(404, "Producto no encontrado")
    return obj

def actualizar_producto(db: Session, producto_id: int, data: schemas.ProductoUpdate) -> Producto:
    obj = obtener_producto(db, producto_id)
    payload = data.model_dump(exclude_none=True)
    if "categoria_id" in payload:
        _ = obtener_categoria(db, payload["categoria_id"])
    for k, v in payload.items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

def borrar_producto(db: Session, producto_id: int) -> None:
    obj = obtener_producto(db, producto_id)
    db.delete(obj); db.commit()

def productos_bajo_stock(db: Session) -> List[Producto]:
    return db.query(Producto).filter(Producto.stock <= Producto.stock_minimo).all()

# --------- Clientes ---------
def crear_cliente(db: Session, data: schemas.ClienteCreate) -> Cliente:
    # Unicidad por cédula
    if db.query(Cliente).filter(Cliente.cedula == data.cedula).first():
        raise HTTPException(400, "Ya existe un cliente con esa cédula")
    obj = Cliente(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def listar_clientes(db: Session) -> List[Cliente]:
    return db.query(Cliente).all()

def obtener_cliente(db: Session, cliente_id: int) -> Cliente:
    obj = db.query(Cliente).get(cliente_id)
    if not obj: raise HTTPException(404, "Cliente no encontrado")
    return obj

def actualizar_cliente(db: Session, cliente_id: int, data: schemas.ClienteUpdate) -> Cliente:
    obj = obtener_cliente(db, cliente_id)
    payload = data.model_dump(exclude_none=True)
    # si cambia cédula, validar unicidad
    if "cedula" in payload:
        existe = db.query(Cliente).filter(Cliente.cedula == payload["cedula"], Cliente.id != cliente_id).first()
        if existe:
            raise HTTPException(400, "Ya existe otro cliente con esa cédula")
    for k, v in payload.items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

def borrar_cliente(db: Session, cliente_id: int) -> None:
    obj = obtener_cliente(db, cliente_id)
    db.delete(obj); db.commit()

# --------- Usuarios ---------
def crear_usuario(db: Session, data: schemas.UsuarioCreate) -> Usuario:
    if db.query(Usuario).filter(Usuario.cedula == data.cedula).first():
        raise HTTPException(400, "Ya existe un usuario con esa cédula")
    obj = Usuario(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def listar_usuarios(db: Session) -> List[Usuario]:
    return db.query(Usuario).all()

def obtener_usuario(db: Session, usuario_id: int) -> Usuario:
    obj = db.query(Usuario).get(usuario_id)
    if not obj: raise HTTPException(404, "Usuario no encontrado")
    return obj

def actualizar_usuario(db: Session, usuario_id: int, data: schemas.UsuarioUpdate) -> Usuario:
    obj = obtener_usuario(db, usuario_id)
    payload = data.model_dump(exclude_none=True)
    if "cedula" in payload:
        existe = db.query(Usuario).filter(Usuario.cedula == payload["cedula"], Usuario.id != usuario_id).first()
        if existe:
            raise HTTPException(400, "Ya existe otro usuario con esa cédula")
    for k, v in payload.items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

def borrar_usuario(db: Session, usuario_id: int) -> None:
    obj = obtener_usuario(db, usuario_id)
    db.delete(obj); db.commit()

# --------- Compras ---------
def crear_compra(db: Session, data: schemas.CompraCreate) -> Compra:
    cliente = db.query(Cliente).get(data.cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")

    producto = db.query(Producto).get(data.producto_id)
    if not producto:
        raise HTTPException(404, "Producto no encontrado")

    if data.cantidad <= 0:
        raise HTTPException(400, "La cantidad debe ser mayor a 0")

    if producto.stock < data.cantidad:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuficiente")

    producto.stock -= data.cantidad
    compra = Compra(**data.model_dump())

    db.add(compra); db.add(producto)
    db.commit(); db.refresh(compra)
    return compra

def listar_compras(db: Session) -> List[Compra]:
    return db.query(Compra).order_by(Compra.fecha.desc()).all()

def obtener_compra(db: Session, compra_id: int) -> Compra:
    obj = db.query(Compra).get(compra_id)
    if not obj: raise HTTPException(404, "Compra no encontrada")
    return obj

def borrar_compra(db: Session, compra_id: int) -> None:
    obj = obtener_compra(db, compra_id)
    db.delete(obj); db.commit()
