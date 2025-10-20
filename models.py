# models.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, Numeric, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from database import Base


# ==========================
# CATEGORIA
# ==========================
class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    # código visible (opcional) pero único si se usa
    codigo = Column(String(30), unique=True, index=True, nullable=True)
    nombre = Column(String(120), nullable=False, index=True)   # <- dejamos SOLO este index, sin Index() manual

    # timestamps (opcional)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # relación 1:N con productos
    productos = relationship("Producto", back_populates="categoria")

    __table_args__ = (
        UniqueConstraint("codigo", name="uq_categorias_codigo"),
        # ¡OJO! No agregar Index("ix_categorias_nombre", "nombre") para evitar duplicados
    )


# ==========================
# PRODUCTO
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

    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_productos_stock_no_negativo"),
        CheckConstraint("umbral_mayor >= 0", name="ck_productos_umbral_no_negativo"),
        # Índice compuesto útil y NO duplicado (diferente a los índices individuales)
        Index("ix_productos_nombre_stock", "nombre", "stock"),
    )


# ==========================
# USUARIO (opcional 1:1 con Cliente)
# ==========================
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    cedula = Column(String(20), unique=True, index=True, nullable=False)
    tipo = Column(String(20), nullable=False, index=True)  # 'mayorista' | 'minorista'
    cliente_frecuente = Column(Boolean, default=False, index=True)

    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relación 1:1 opcional con Cliente
    cliente = relationship("Cliente", back_populates="usuario", uselist=False)

    __table_args__ = (
        CheckConstraint("tipo IN ('mayorista','minorista')", name="ck_usuarios_tipo_valido"),
        Index("ix_usuarios_tipo_frecuente", "tipo", "cliente_frecuente"),
    )


# ==========================
# CLIENTE
# ==========================
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)

    # Para compatibilidad con tu CRUD actual
    cedula = Column(String(20), unique=True, index=True, nullable=True)

    # Enlace opcional 1:1 con Usuario (si lo usas en tus routers)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=True, index=True)
    usuario = relationship("Usuario", back_populates="cliente", uselist=False)

    telefono = Column(String(30), nullable=True)
    direccion = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True, index=True)

    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 1:N con Compra
    compras = relationship("Compra", back_populates="cliente", cascade="all, delete")


# ==========================
# COMPRA (según tu CRUD actual)
# ==========================
class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False)

    # Tu CRUD ordena por este campo
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)

    cliente = relationship("Cliente", back_populates="compras")
    producto = relationship("Producto")

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_compras_cantidad_positiva"),
    )
