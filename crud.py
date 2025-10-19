from typing import List, Optional, Tuple, Dict
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models import Categoria, Producto, Cliente, Compra, Usuario
import schemas

# ==============================
# -------- CATEGORÍAS ----------
# ==============================

async def crear_categoria(db: AsyncSession, data: schemas.CategoriaCreate) -> Categoria:
    q = await db.execute(select(Categoria).where(Categoria.nombre == data.nombre))
    if q.scalar_one_or_none():
        raise HTTPException(400, "La categoría ya existe")
    obj = Categoria(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def listar_categorias(db: AsyncSession) -> List[Categoria]:
    q = await db.execute(select(Categoria))
    return q.scalars().all()

async def obtener_categoria(db: AsyncSession, categoria_id: int) -> Categoria:
    q = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Categoría no encontrada")
    return obj

async def actualizar_categoria(db: AsyncSession, categoria_id: int, data: schemas.CategoriaUpdate) -> Categoria:
    obj = await obtener_categoria(db, categoria_id)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def borrar_categoria(db: AsyncSession, categoria_id: int) -> None:
    obj = await obtener_categoria(db, categoria_id)
    await db.delete(obj)
    await db.commit()

# NEW: filtrar categorías por nombre y devolver códigos (o estructura completa)
async def filtrar_categorias_por_nombre(
    db: AsyncSession,
    nombre: str,
    solo_codigos: bool = True
) -> List[Dict[str, str]]:
    q = await db.execute(
        select(Categoria).where(Categoria.nombre.ilike(f"%{nombre}%"))
    )
    cats = q.scalars().all()
    if solo_codigos:
        return [{"codigo": (c.codigo if getattr(c, "codigo", None) else str(c.id))} for c in cats]
    return [{"id": c.id, "codigo": getattr(c, "codigo", None), "nombre": c.nombre} for c in cats]


# ==============================
# --------- PRODUCTOS ----------
# ==============================

async def crear_producto(db: AsyncSession, data: schemas.ProductoCreate) -> Producto:
    # valida FK categoría si viene
    if data.categoria_id is not None:
        await obtener_categoria(db, data.categoria_id)
    obj = Producto(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

# NEW: listado con filtros (nombre contiene, min_stock)
async def listar_productos(
    db: AsyncSession,
    nombre: Optional[str] = None,
    min_stock: Optional[int] = None
) -> List[Producto]:
    stmt = select(Producto)
    if nombre:
        stmt = stmt.where(Producto.nombre.ilike(f"%{nombre}%"))
    if min_stock is not None:
        stmt = stmt.where(Producto.stock >= min_stock)
    q = await db.execute(stmt)
    return q.scalars().all()

async def obtener_producto(db: AsyncSession, producto_id: int) -> Producto:
    q = await db.execute(select(Producto).where(Producto.id == producto_id))
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Producto no encontrado")
    return obj

async def actualizar_producto(db: AsyncSession, producto_id: int, data: schemas.ProductoUpdate) -> Producto:
    obj = await obtener_producto(db, producto_id)
    payload = data.model_dump(exclude_none=True)
    if "categoria_id" in payload and payload["categoria_id"] is not None:
        await obtener_categoria(db, payload["categoria_id"])
    for k, v in payload.items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def borrar_producto(db: AsyncSession, producto_id: int) -> None:
    obj = await obtener_producto(db, producto_id)
    await db.delete(obj)
    await db.commit()

async def productos_bajo_stock(db: AsyncSession) -> List[Producto]:
    # OJO: requiere que tu modelo tenga 'stock_minimo'. Si no, elimínalo o ajústalo.
    q = await db.execute(select(Producto).where(Producto.stock <= Producto.stock_minimo))
    return q.scalars().all()

# NEW: cálculo de precio por cantidad aplicando umbral_mayor/valor_unitario_mayor
async def calcular_precio_para_cantidad(
    db: AsyncSession,
    producto_id: int,
    cantidad: int
) -> Tuple[Decimal, Decimal]:
    """
    Devuelve (precio_unitario_aplicado, total).
    Regla: si cantidad > umbral_mayor y existe valor_unitario_mayor, usar ese precio.
    """
    if cantidad <= 0:
        raise HTTPException(400, "Cantidad debe ser > 0")

    prod = await obtener_producto(db, producto_id)
    precio_unit = prod.valor_unitario
    umbral = prod.umbral_mayor or 20
    if cantidad > umbral and getattr(prod, "valor_unitario_mayor", None) is not None:
        precio_unit = prod.valor_unitario_mayor

    # asegurar Decimal con 2 decimales
    pu = Decimal(str(precio_unit))
    total = (pu * Decimal(cantidad)).quantize(Decimal("0.01"))
    return pu, total


# ==============================
# ---------- CLIENTES ----------
# ==============================

async def crear_cliente(db: AsyncSession, data: schemas.ClienteCreate) -> Cliente:
    q = await db.execute(select(Cliente).where(Cliente.cedula == data.cedula))
    if q.scalar_one_or_none():
        raise HTTPException(400, "Ya existe un cliente con esa cédula")
    obj = Cliente(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def listar_clientes(db: AsyncSession) -> List[Cliente]:
    q = await db.execute(select(Cliente))
    return q.scalars().all()

async def obtener_cliente(db: AsyncSession, cliente_id: int) -> Cliente:
    q = await db.execute(select(Cliente).where(Cliente.id == cliente_id))
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Cliente no encontrado")
    return obj

async def actualizar_cliente(db: AsyncSession, cliente_id: int, data: schemas.ClienteUpdate) -> Cliente:
    obj = await obtener_cliente(db, cliente_id)
    payload = data.model_dump(exclude_none=True)
    if "cedula" in payload:
        q = await db.execute(select(Cliente).where(Cliente.cedula == payload["cedula"], Cliente.id != cliente_id))
        if q.scalar_one_or_none():
            raise HTTPException(400, "Ya existe otro cliente con esa cédula")
    for k, v in payload.items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def borrar_cliente(db: AsyncSession, cliente_id: int) -> None:
    obj = await obtener_cliente(db, cliente_id)
    await db.delete(obj)
    await db.commit()


# ==============================
# ---------- USUARIOS ----------
# ==============================

async def crear_usuario(db: AsyncSession, data: schemas.UsuarioCreate) -> Usuario:
    q = await db.execute(select(Usuario).where(Usuario.cedula == data.cedula))
    if q.scalar_one_or_none():
        raise HTTPException(400, "Ya existe un usuario con esa cédula")
    obj = Usuario(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

# NEW: listado con filtros tipo/cedula/frecuente
async def listar_usuarios(
    db: AsyncSession,
    tipo: Optional[str] = None,          # 'mayorista' | 'minorista'
    cedula: Optional[str] = None,        # exacta
    frecuente: Optional[bool] = None     # True/False
) -> List[Usuario]:
    stmt = select(Usuario)
    if tipo:
        stmt = stmt.where(Usuario.tipo == tipo)
    if cedula:
        stmt = stmt.where(Usuario.cedula == cedula)
    if frecuente is not None:
        stmt = stmt.where(Usuario.cliente_frecuente == frecuente)
    q = await db.execute(stmt)
    return q.scalars().all()

# NEW: obtener por cédula
async def obtener_usuario_por_cedula(db: AsyncSession, cedula: str) -> Usuario:
    q = await db.execute(select(Usuario).where(Usuario.cedula == cedula))
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Usuario no encontrado")
    return obj

async def obtener_usuario(db: AsyncSession, usuario_id: int) -> Usuario:
    q = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Usuario no encontrado")
    return obj

async def actualizar_usuario(db: AsyncSession, usuario_id: int, data: schemas.UsuarioUpdate) -> Usuario:
    obj = await obtener_usuario(db, usuario_id)
    payload = data.model_dump(exclude_none=True)
    if "cedula" in payload:
        q = await db.execute(select(Usuario).where(Usuario.cedula == payload["cedula"], Usuario.id != usuario_id))
        if q.scalar_one_or_none():
            raise HTTPException(400, "Ya existe otro usuario con esa cédula")
    for k, v in payload.items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def borrar_usuario(db: AsyncSession, usuario_id: int) -> None:
    obj = await obtener_usuario(db, usuario_id)
    await db.delete(obj)
    await db.commit()


# ==============================
# ---------- COMPRAS -----------
# ==============================

async def crear_compra(db: AsyncSession, data: schemas.CompraCreate) -> Compra:
    # valida cliente
    qcli = await db.execute(select(Cliente).where(Cliente.id == data.cliente_id))
    cliente = qcli.scalar_one_or_none()
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")

    # valida producto
    qpro = await db.execute(select(Producto).where(Producto.id == data.producto_id))
    producto = qpro.scalar_one_or_none()
    if not producto:
        raise HTTPException(404, "Producto no encontrado")

    if data.cantidad <= 0:
        raise HTTPException(400, "La cantidad debe ser mayor a 0")

    if producto.stock < data.cantidad:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Stock insuficiente")

    # DESCUENTO DE STOCK
    producto.stock -= data.cantidad

    # Si quieres guardar el precio aplicado aquí, añade campos en tu modelo/esquema de Compra.
    # Puedes calcularlo reutilizando la lógica de precio por cantidad:
    # pu, total = await calcular_precio_para_cantidad(db, producto.id, data.cantidad)
    # compra = Compra(**data.model_dump(), precio_unitario_aplicado=pu, total=total)
    # Por ahora, mantengo tu estructura original:

    compra = Compra(**data.model_dump())

    db.add(compra)
    db.add(producto)
    await db.commit()
    await db.refresh(compra)
    return compra

async def listar_compras(db: AsyncSession) -> List[Compra]:
    q = await db.execute(select(Compra).order_by(Compra.fecha.desc()))
    return q.scalars().all()

async def obtener_compra(db: AsyncSession, compra_id: int) -> Compra:
    q = await db.execute(select(Compra).where(Compra.id == compra_id))
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Compra no encontrada")
    return obj

async def borrar_compra(db: AsyncSession, compra_id: int) -> None:
    obj = await obtener_compra(db, compra_id)
    await db.delete(obj)
    await db.commit()
