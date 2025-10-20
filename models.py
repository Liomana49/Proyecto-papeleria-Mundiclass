# models.py
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, Numeric, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# ==========================
# CATEGORIAS
# ==========================
class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False, index=True)
    codigo = Column(String(30), nullable=True, index=True)

    # Marca de tiempo (para evitar NOT NULL)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    productos = relationship("Producto", back_populates="categoria")

    __table_args__ = (
        UniqueConstraint("codigo", name="uq_categorias_codigo"),
        # Evitamos índices duplicados (ya hay index=True en 'nombre')
    )


# ==========================
# PRODUCTOS
# ==========================
class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False, index=True)
    stock = Column(Integer, default=0, nullable=False, index=True)

    valor_unitario = Column(Numeric(10, 2), nullable=False)
    valor_unitario_mayor = Column(Numeric(10, 2), nullable=True)
    umbral_mayor = Column(Integer, default=20, nullable=False)

    activo = Column(Boolean, default=True, index=True)

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    categoria = relationship("Categoria", back_populates="productos")

    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_productos_stock_no_negativo"),
        CheckConstraint("umbral_mayor >= 0", name="ck_productos_umbral_no_negativo"),
        Index("ix_productos_nombre_stock", "nombre", "stock"),
    )


# ==========================
# USUARIOS
# ==========================
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    cedula = Column(String(20), unique=True, index=True, nullable=False)
    tipo = Column(String(20), nullable=False, index=True)  # 'mayorista' | 'minorista'
    cliente_frecuente = Column(Boolean, default=False, index=True)

    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relación 1:1 opcional con Cliente
    cliente = relationship("Cliente", back_populates="usuario", uselist=False)

    __table_args__ = (
        CheckConstraint("tipo IN ('mayorista','minorista')", name="ck_usuarios_tipo_valido"),
        Index("ix_usuarios_tipo_frecuente", "tipo", "cliente_frecuente"),
    )


# ==========================
# CLIENTES
# ==========================
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)

    # Para compatibilidad con tu CRUD/routers
    cedula = Column(String(20), unique=True, index=True, nullable=True)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=True, index=True)
    usuario = relationship("Usuario", back_populates="cliente", uselist=False)

    telefono = Column(String(30), nullable=True)
    direccion = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True, index=True)

    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    compras = relationship("Compra", back_populates="cliente", cascade="all, delete")


# ==========================
# COMPRAS
# ==========================
class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False)

    # Tu CRUD ordena por este campo
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cliente = relationship("Cliente", back_populates="compras")
    producto = relationship("Producto")

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_compras_cantidad_positiva"),
    )


# ==========================
# HISTORIAL DE ELIMINADOS
# ==========================
class HistorialEliminados(Base):
    __tablename__ = "historial_eliminados"

    id = Column(Integer, primary_key=True, index=True)
    tabla = Column(String, nullable=False)          # p.ej., 'Usuario', 'Producto', etc.
    registro_id = Column(Integer, nullable=False)   # ID del registro eliminado
    descripcion = Column(String, nullable=True)
    fecha_eliminado = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


