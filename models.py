from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum, UniqueConstraint, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from enum import Enum
from database import Base
from datetime import datetime

class TipoCliente(str, Enum):
    mayorista = "mayorista"
    minorista = "minorista"

class RolUsuario(str, Enum):
    administrador = "administrador"
    vendedor = "vendedor"
    proveedor = "proveedor"
    cliente = "cliente"

class Categoria(Base):
    _tablename_ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    imagen_url = Column(String, nullable=True)

    productos = relationship("Producto", back_populates="categoria")

class Producto(Base):
    _tablename_ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    imagen_url = Column(String, nullable=True)
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=0)

    categoria = relationship("Categoria", back_populates="productos")
    compras = relationship("Compra", back_populates="producto")

class Cliente(Base):
    _tablename_ = "clientes"
    _table_args_ = (
        UniqueConstraint("cedula", name="uq_clientes_cedula"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    cedula = Column(String(30), nullable=False, index=True)
    tipo = Column(SAEnum(TipoCliente), nullable=False, default=TipoCliente.minorista)
    es_potencial = Column(Boolean, default=False)
    frecuencia_compra_dias = Column(Integer, nullable=True)

    compras = relationship("Compra", back_populates="cliente")

class Usuario(Base):
    _tablename_ = "usuarios"
    _table_args_ = (
        UniqueConstraint("cedula", name="uq_usuarios_cedula"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    cedula = Column(String(30), nullable=False, index=True)
    rol = Column(SAEnum(RolUsuario), nullable=False, default=RolUsuario.vendedor)

class Compra(Base):
    _tablename_ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)

    cliente = relationship("Cliente", back_populates="compras")
    producto = relationship("Producto", back_populates="compras")