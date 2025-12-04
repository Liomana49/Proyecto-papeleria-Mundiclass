# crud.py
from typing import List, Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

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
    await db.refresh(obj) # 🔄 Línea AÑADIDA para refrescar el objeto después del commit

    # Load multimedia to avoid lazy loading issues during serialization
    stmt = select(Usuario).where(Usuario.id == obj.id).options(selectinload(Usuario.multimedia))
    q = await db.execute(stmt)
    obj = q.scalar_one()
    return obj


async def listar_usuarios(
    db: AsyncSession,
    nombre: Optional[str] = None,
    correo: Optional[str] = None,
    cedula: Optional[str] = None,
    rol: Optional[str] = None,
    tipo: Optional[str] = None,
    cliente_frecuente: Optional[bool] = None,
) -> List[Usuario]:
    stmt = select(Usuario)

    if nombre:
        stmt = stmt.where(Usuario.nombre.ilike(f"%{nombre}%"))
    if correo:
        stmt = stmt.where(Usuario.correo.ilike(f"%{correo}%"))
    if cedula:
        stmt = stmt.where(Usuario.cedula.ilike(f"%{cedula}%"))
    if rol:
        stmt = stmt.where(Usuario.rol == rol)
    if tipo:
        stmt = stmt.where(Usuario.tipo == tipo)
    if cliente_frecuente is not None:
        stmt = stmt.where(Usuario.cliente_frecuente == cliente_frecuente)

    q = await db.execute(stmt)
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
    await db.refresh(obj) # 🔄 Línea AÑADIDA para refrescar el objeto después del commit

    # Load multimedia to avoid lazy loading issues during serialization
    stmt = select(Usuario).where(Usuario.id == obj.id).options(selectinload(Usuario.multimedia))
    q = await db.execute(stmt)
    obj = q.scalar_one()
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
    await db.refresh(obj) # 🔄 Refresco después del commit

    # Load multimedia to avoid lazy loading issues during serialization
    stmt = select(Cliente).where(Cliente.id == obj.id).options(selectinload(Cliente.multimedia))
    q = await db.execute(stmt)
    obj = q.scalar_one()
    return obj


async def listar_clientes(
    db: AsyncSession,
    nombre: Optional[str] = None,
    cedula: Optional[str] = None,
    tipo_cliente: Optional[str] = None,
    cliente_frecuente: Optional[bool] = None,
) -> List[Cliente]:
    stmt = select(Cliente).options(joinedload(Cliente.usuario), selectinload(Cliente.multimedia))

    if nombre:
        stmt = stmt.where(Cliente.nombre.ilike(f"%{nombre}%"))
    if cedula:
        stmt = stmt.where(Cliente.cedula.ilike(f"%{cedula}%"))
    if tipo_cliente:
        stmt = stmt.where(Cliente.tipo_cliente == tipo_cliente)
    if cliente_frecuente is not None:
        stmt = stmt.where(Cliente.cliente_frecuente == cliente_frecuente)

    q = await db.execute(stmt)
    return q.scalars().all()


async def obtener_cliente(db: AsyncSession, cliente_id: int) -> Cliente:
    q = await db.execute(
        select(Cliente)
        .where(Cliente.id == cliente_id)
        .options(joinedload(Cliente.usuario).selectinload(Usuario.multimedia), selectinload(Cliente.multimedia))
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
    # ❌ LÍNEA ELIMINADA: await db.refresh(obj)

    # Return a fresh object with all relationships loaded to avoid lazy loading issues
    stmt = select(Cliente).where(Cliente.id == cliente_id).options(
        joinedload(Cliente.usuario).selectinload(Usuario.multimedia),
        selectinload(Cliente.multimedia)
    )
    q = await db.execute(stmt)
    return q.scalar_one()

async def borrar_cliente(db: AsyncSession, cliente_id: int) -> None:
    from sqlalchemy import select
    
    # Obtener sin cargar multimedia para evitar greenlet error
    q = await db.execute(
        select(Cliente).where(Cliente.id == cliente_id)
        .options(selectinload(Cliente.compras))
    )
    obj = q.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(404, "Cliente no encontrado")

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

    # Verificar código único si fue proporcionado
    if getattr(data, 'codigo', None):
        q2 = await db.execute(select(Categoria).where(Categoria.codigo == data.codigo))
        if q2.scalar_one_or_none():
            raise HTTPException(400, "Ya existe una categoría con ese código")

    obj = Categoria(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def listar_categorias(
    db: AsyncSession,
    nombre: Optional[str] = None,
    codigo: Optional[str] = None,
) -> List[Categoria]:
    stmt = select(Categoria)

    if nombre:
        stmt = stmt.where(Categoria.nombre.ilike(f"%{nombre}%"))
    if codigo:
        stmt = stmt.where(Categoria.codigo.ilike(f"%{codigo}%"))

    q = await db.execute(stmt)
    return q.scalars().all()


async def obtener_categoria(db: AsyncSession, categoria_id: int) -> Categoria:
    # Aseguramos la carga ávida de productos si van a ser eliminados en cascada.
    q = await db.execute(select(Categoria).where(Categoria.id == categoria_id).options(selectinload(Categoria.productos)))
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

    # Verificar código único si se está actualizando
    if "codigo" in update_data and update_data["codigo"] is not None:
        q3 = await db.execute(
            select(Categoria).where(
                Categoria.codigo == update_data["codigo"],
                Categoria.id != categoria_id,
            )
        )
        if q3.scalar_one_or_none():
            raise HTTPException(
                400,
                "Ya existe otra categoría con ese código",
            )

    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def borrar_categoria(db: AsyncSession, categoria_id: int) -> None:
    obj = await obtener_categoria(db, categoria_id)
    
    # 🚀 NUEVA LÓGICA: Eliminar en cascada los productos asociados.

    # Convertir a lista para poder iterar y borrar sin problemas de mutación
    productos_a_eliminar = list(obj.productos)
    
    for producto in productos_a_eliminar:
        # Registrar producto en historial (usamos la misma lógica que en borrar_producto)
        datos_producto = {
            "id": producto.id,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "cantidad": producto.cantidad,
            "valor_unitario": producto.valor_unitario,
            "valor_mayorista": producto.valor_mayorista,
            "categoria_id": producto.categoria_id,
            "creado_en": producto.creado_en.isoformat() if producto.creado_en else None,
            "actualizado_en": producto.actualizado_en.isoformat() if producto.actualizado_en else None,
        }
        await _registrar_eliminado(db, "productos", producto.id, datos_producto)
        
        # Eliminar producto de la sesión
        await db.delete(producto)
        
    # Registrar y eliminar la categoría
    datos_categoria = {
        "id": obj.id,
        "nombre": obj.nombre,
        "codigo": obj.codigo,
        "creado_en": obj.creado_en.isoformat() if obj.creado_en else None,
        "actualizado_en": obj.actualizado_en.isoformat() if obj.actualizado_en else None,
    }

    await _registrar_eliminado(db, "categorias", obj.id, datos_categoria)
    await db.delete(obj)
    await db.commit() # Commit de toda la transacción


# ======================================================
# ===================== PRODUCTOS ======================
# ======================================================

async def crear_producto(db: AsyncSession, data: schemas.ProductoCreate) -> Producto:
    # Si viene categoría, validar que exista
    if data.categoria_id is not None:
        await obtener_categoria(db, data.categoria_id) # Llamada a obtener_categoria no cargada

    obj = Producto(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def listar_productos(
    db: AsyncSession,
    nombre: Optional[str] = None,
    categoria_id: Optional[int] = None,
    precio_min: Optional[float] = None,
    precio_max: Optional[float] = None,
    stock_min: Optional[int] = None,
    stock_max: Optional[int] = None,
) -> List[Producto]:
    stmt = select(Producto).options(joinedload(Producto.categoria))

    if nombre:
        stmt = stmt.where(Producto.nombre.ilike(f"%{nombre}%"))
    if categoria_id is not None:
        stmt = stmt.where(Producto.categoria_id == categoria_id)
    if precio_min is not None:
        stmt = stmt.where(Producto.valor_unitario >= precio_min)
    if precio_max is not None:
        stmt = stmt.where(Producto.valor_unitario <= precio_max)
    if stock_min is not None:
        stmt = stmt.where(Producto.cantidad >= stock_min)
    if stock_max is not None:
        stmt = stmt.where(Producto.cantidad <= stock_max)

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
    from sqlalchemy import select
    
    # Obtener sin cargar multimedia para evitar greenlet error
    q = await db.execute(
        select(Producto).where(Producto.id == producto_id)
        .options(selectinload(Producto.compras))
    )
    obj = q.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(404, "Producto no encontrado")

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
    await db.refresh(obj, ["cliente", "producto"])
    return obj


async def listar_compras(
    db: AsyncSession,
    cliente_id: Optional[int] = None,
    producto_id: Optional[int] = None,
    min_total: Optional[float] = None,
    max_total: Optional[float] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    nombre_cliente: Optional[str] = None,
    nombre_producto: Optional[str] = None,
) -> List[Compra]:
    stmt = select(Compra).options(
        joinedload(Compra.cliente),
        joinedload(Compra.producto),
    )

    if cliente_id is not None:
        stmt = stmt.where(Compra.cliente_id == cliente_id)
    if producto_id is not None:
        stmt = stmt.where(Compra.producto_id == producto_id)
    if min_total is not None:
        stmt = stmt.where(Compra.total >= min_total)
    if max_total is not None:
        stmt = stmt.where(Compra.total <= max_total)
    if fecha_desde:
        stmt = stmt.where(Compra.fecha >= fecha_desde)
    if fecha_hasta:
        stmt = stmt.where(Compra.fecha <= fecha_hasta)
    if nombre_cliente:
        stmt = stmt.where(Compra.cliente.has(Cliente.nombre.ilike(f"%{nombre_cliente}%")))
    if nombre_producto:
        stmt = stmt.where(Compra.producto.has(Producto.nombre.ilike(f"%{nombre_producto}%")))

    q = await db.execute(stmt)
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


async def actualizar_compra(db: AsyncSession, compra_id: int, data: schemas.CompraUpdate) -> Compra:
    obj = await obtener_compra(db, compra_id)
    
    # Si se cambió la cantidad, ajustar el stock del producto
    if data.cantidad is not None and data.cantidad != obj.cantidad:
        diff = obj.cantidad - data.cantidad
        obj.producto.cantidad += diff
    
    # Actualizar campos
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    
    await db.commit()
    await db.refresh(obj)
    return obj


async def borrar_compra(db: AsyncSession, compra_id: int) -> None:
    from sqlalchemy import select
    
    # Obtener con producto para revertir stock
    q = await db.execute(
        select(Compra).where(Compra.id == compra_id)
        .options(selectinload(Compra.producto))
    )
    obj = q.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(404, "Compra no encontrada")

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