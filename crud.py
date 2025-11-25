# crud.py
from typing import List, Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models import (
    Usuario,
    Cliente,
    Categoria,
    Producto,
    Compra,
    HistorialEliminados,
)
import schemas


# ======================================================
# ===============   HELPER GENÉRICO   ==================
# ======================================================

async def _registrar_eliminado(
    db: AsyncSession,
    tabla: str,
    registro_id: int,
    datos: Dict[str, Any],
) -> None:
    """
    Crea un registro en HistorialEliminados con un snapshot del objeto borrado.
    """
    log = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos=datos,
    )
    db.add(log)
    # NO commit aquí solo – el commit final se hace en la función que borra
    # para que todo quede en una sola transacción.


# ======================================================
# ===================== USUARIOS =======================
# ======================================================

async def crear_usuario(db: AsyncSession, data: schemas.UsuarioCreate) -> Usuario:
    # Validar correo y cédula únicos
    q = await db.execute(select(Usuario).where(Usuario.correo == data.correo))
    if q.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese correo",
        )

    q = await db.execute(select(Usuario).where(Usuario.cedula == data.cedula))
    if q.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con esa cédula",
        )

    obj = Usuario(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def listar_usuarios(db: AsyncSession) -> List[Usuario]:
    q = await db.execute(select(Usuario))
    return q.scalars().all()


async def obtener_usuario(db: AsyncSession, usuario_id: int) -> Usuario:
    q = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return obj


async def actualizar_usuario(
    db: AsyncSession, usuario_id: int, data: schemas.UsuarioUpdate
) -> Usuario:
    obj = await obtener_usuario(db, usuario_id)
    update_data = data.model_dump(exclude_unset=True)

    # Si cambia correo o cédula, validar duplicados
    if "correo" in update_data:
        q = await db.execute(
            select(Usuario).where(
                Usuario.correo == update_data["correo"],
                Usuario.id != usuario_id,
            )
        )
        if q.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro usuario con ese correo",
            )

    if "cedula" in update_data:
        q = await db.execute(
            select(Usuario).where(
                Usuario.cedula == update_data["cedula"],
                Usuario.id != usuario_id,
            )
        )
        if q.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro usuario con esa cédula",
            )

    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def borrar_usuario(db: AsyncSession, usuario_id: int) -> None:
    obj = await obtener_usuario(db, usuario_id)

    # Opcional: verificar si tiene clientes asociados
    if obj.clientes:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el usuario porque tiene clientes asociados",
        )

    datos = {
        "id": obj.id,
        "nombre": obj.nombre,
        "correo": obj.correo,
        "rol": obj.rol,
        "cedula": obj.cedula,
        "tipo": obj.tipo,
        "cliente_frecuente": obj.cliente_frecuente,
        "creado_en": obj.creado_en.isoformat() if obj.creado_en else None,
        "actualizado_en": obj.actualizado_en.isoformat() if obj.actualizado_en else None,
    }

    await _registrar_eliminado(db, "usuarios", obj.id, datos)
    await db.delete(obj)
    await db.commit()


# ======================================================
# ===================== CLIENTES =======================
# ======================================================

async def crear_cliente(db: AsyncSession, data: schemas.ClienteCreate) -> Cliente:
    # Validar cédula única
    q = await db.execute(select(Cliente).where(Cliente.cedula == data.cedula))
    if q.scalar_one_or_none():
        raise HTTPException(400, "Ya existe un cliente con esa cédula")

    # Si viene usuario_id, validar que exista
    if data.usuario_id is not None:
        await obtener_usuario(db, data.usuario_id)

    obj = Cliente(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def listar_clientes(db: AsyncSession) -> List[Cliente]:
    q = await db.execute(
        select(Cliente).options(joinedload(Cliente.usuario))
    )
    return q.scalars().all()


async def obtener_cliente(db: AsyncSession, cliente_id: int) -> Cliente:
    q = await db.execute(
        select(Cliente)
        .where(Cliente.id == cliente_id)
        .options(joinedload(Cliente.usuario))
    )
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Cliente no encontrado")
    return obj


async def actualizar_cliente(
    db: AsyncSession, cliente_id: int, data: schemas.ClienteUpdate
) -> Cliente:
    obj = await obtener_cliente(db, cliente_id)
    update_data = data.model_dump(exclude_unset=True)

    if "cedula" in update_data:
        q = await db.execute(
            select(Cliente).where(
                Cliente.cedula == update_data["cedula"],
                Cliente.id != cliente_id,
            )
        )
        if q.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro cliente con esa cédula",
            )

    if "usuario_id" in update_data and update_data["usuario_id"] is not None:
        await obtener_usuario(db, update_data["usuario_id"])

    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def borrar_cliente(db: AsyncSession, cliente_id: int) -> None:
    obj = await obtener_cliente(db, cliente_id)

    # Opcional: bloquear si tiene compras
    if obj.compras:
        raise HTTPException(
            400,
            "No se puede eliminar el cliente porque tiene compras registradas",
        )

    datos = {
        "id": obj.id,
        "nombre": obj.nombre,
        "cedula": obj.cedula,
        "tipo_cliente": obj.tipo_cliente,
        "cliente_frecuente": obj.cliente_frecuente,
        "usuario_id": obj.usuario_id,
        "creado_en": obj.creado_en.isoformat() if obj.creado_en else None,
    }

    await _registrar_eliminado(db, "clientes", obj.id, datos)
    await db.delete(obj)
    await db.commit()


# ======================================================
# ==================== CATEGORÍAS ======================
# ======================================================

async def crear_categoria(db: AsyncSession, data: schemas.CategoriaCreate) -> Categoria:
    q = await db.execute(select(Categoria).where(Categoria.nombre == data.nombre))
    if q.scalar_one_or_none():
        raise HTTPException(400, "Ya existe una categoría con ese nombre")

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


async def actualizar_categoria(
    db: AsyncSession, categoria_id: int, data: schemas.CategoriaUpdate
) -> Categoria:
    obj = await obtener_categoria(db, categoria_id)
    update_data = data.model_dump(exclude_unset=True)

    if "nombre" in update_data:
        q = await db.execute(
            select(Categoria).where(
                Categoria.nombre == update_data["nombre"],
                Categoria.id != categoria_id,
            )
        )
        if q.scalar_one_or_none():
            raise HTTPException(
                400,
                "Ya existe otra categoría con ese nombre",
            )

    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def borrar_categoria(db: AsyncSession, categoria_id: int) -> None:
    obj = await obtener_categoria(db, categoria_id)

    # Verificar si tiene productos asociados
    if obj.productos:
        raise HTTPException(
            400,
            "No se puede eliminar la categoría porque tiene productos asociados",
        )

    datos = {
        "id": obj.id,
        "nombre": obj.nombre,
        "codigo": obj.codigo,
        "creado_en": obj.creado_en.isoformat() if obj.creado_en else None,
        "actualizado_en": obj.actualizado_en.isoformat() if obj.actualizado_en else None,
    }

    await _registrar_eliminado(db, "categorias", obj.id, datos)
    await db.delete(obj)
    await db.commit()


# ======================================================
# ===================== PRODUCTOS ======================
# ======================================================

async def crear_producto(db: AsyncSession, data: schemas.ProductoCreate) -> Producto:
    # Si viene categoría, validar que exista
    if data.categoria_id is not None:
        await obtener_categoria(db, data.categoria_id)

    obj = Producto(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def listar_productos(
    db: AsyncSession,
    nombre: Optional[str] = None,
    min_stock: Optional[int] = None,
) -> List[Producto]:
    stmt = select(Producto).options(joinedload(Producto.categoria))

    if nombre:
        stmt = stmt.where(Producto.nombre.ilike(f"%{nombre}%"))
    if min_stock is not None:
        stmt = stmt.where(Producto.cantidad >= min_stock)

    q = await db.execute(stmt)
    return q.scalars().all()


async def obtener_producto(db: AsyncSession, producto_id: int) -> Producto:
    q = await db.execute(
        select(Producto)
        .where(Producto.id == producto_id)
        .options(joinedload(Producto.categoria))
    )
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Producto no encontrado")
    return obj


async def actualizar_producto(
    db: AsyncSession, producto_id: int, data: schemas.ProductoUpdate
) -> Producto:
    obj = await obtener_producto(db, producto_id)
    update_data = data.model_dump(exclude_unset=True)

    if "categoria_id" in update_data and update_data["categoria_id"] is not None:
        await obtener_categoria(db, update_data["categoria_id"])

    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def borrar_producto(db: AsyncSession, producto_id: int) -> None:
    obj = await obtener_producto(db, producto_id)

    # Si el producto tiene compras registradas, puedes decidir si bloquear o permitir
    if obj.compras:
        raise HTTPException(
            400,
            "No se puede eliminar el producto porque tiene compras registradas",
        )

    datos = {
        "id": obj.id,
        "nombre": obj.nombre,
        "descripcion": obj.descripcion,
        "cantidad": obj.cantidad,
        "valor_unitario": obj.valor_unitario,
        "valor_mayorista": obj.valor_mayorista,
        "categoria_id": obj.categoria_id,
        "creado_en": obj.creado_en.isoformat() if obj.creado_en else None,
        "actualizado_en": obj.actualizado_en.isoformat() if obj.actualizado_en else None,
    }

    await _registrar_eliminado(db, "productos", obj.id, datos)
    await db.delete(obj)
    await db.commit()


# ======================================================
# ====================== COMPRAS =======================
# ======================================================

async def crear_compra(db: AsyncSession, data: schemas.CompraCreate) -> Compra:
    # Validar cliente y producto
    cliente = await obtener_cliente(db, data.cliente_id)
    producto = await obtener_producto(db, data.producto_id)

    # Validar stock
    if producto.cantidad < data.cantidad:
        raise HTTPException(
            400,
            f"Stock insuficiente. Disponible: {producto.cantidad}",
        )

    # Crear compra
    obj = Compra(**data.model_dump())
    db.add(obj)

    # Actualizar stock del producto
    producto.cantidad -= data.cantidad

    await db.commit()
    await db.refresh(obj)
    return obj


async def listar_compras(db: AsyncSession) -> List[Compra]:
    q = await db.execute(
        select(Compra)
        .options(
            joinedload(Compra.cliente),
            joinedload(Compra.producto),
        )
    )
    return q.scalars().all()


async def obtener_compra(db: AsyncSession, compra_id: int) -> Compra:
    q = await db.execute(
        select(Compra)
        .where(Compra.id == compra_id)
        .options(
            joinedload(Compra.cliente),
            joinedload(Compra.producto),
        )
    )
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Compra no encontrada")
    return obj


async def borrar_compra(db: AsyncSession, compra_id: int) -> None:
    obj = await obtener_compra(db, compra_id)

    # Revertir stock del producto
    producto = obj.producto
    if producto:
        producto.cantidad += obj.cantidad

    datos = {
        "id": obj.id,
        "cliente_id": obj.cliente_id,
        "producto_id": obj.producto_id,
        "cantidad": obj.cantidad,
        "precio_unitario_aplicado": obj.precio_unitario_aplicado,
        "total": obj.total,
        "fecha": obj.fecha.isoformat() if obj.fecha else None,
    }

    await _registrar_eliminado(db, "compras", obj.id, datos)
    await db.delete(obj)
    await db.commit()


# ======================================================
# ============= HISTORIAL ELIMINADOS ===================
# ======================================================

async def listar_historial(db: AsyncSession) -> List[HistorialEliminados]:
    q = await db.execute(
        select(HistorialEliminados).order_by(HistorialEliminados.eliminado_en.desc())
    )
    return q.scalars().all()
