from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

# --------------------------- USUARIO ---------------------------
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    cedula = Column(String, unique=True, nullable=False)
    tipo = Column(String, nullable=False)  # mayorista/minorista
    cliente_frecuente = Column(Boolean, default=False)

# --------------------------- CLIENTE ---------------------------
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    cedula = Column(String, unique=True, nullable=False)
    activo = Column(Boolean, default=True)

# --------------------------- CATEGORIA ---------------------------
class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    codigo = Column(String, nullable=True)

# --------------------------- PRODUCTO ---------------------------
class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    valor_unitario = Column(Float, nullable=False)
    valor_unitario_mayor = Column(Float, nullable=True)
    umbral_mayor = Column(Integer, nullable=True, default=20)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    categoria = relationship("Categoria")

# --------------------------- COMPRA ---------------------------
class Compra(Base):
    __tablename__ = "compras"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())

# --------------------------- HISTORIAL ---------------------------
class HistorialEliminados(Base):
    __tablename__ = "historial_eliminados"
    id = Column(Integer, primary_key=True, index=True)
    tabla = Column(String, nullable=False)
    registro_id = Column(Integer, nullable=False)
    descripcion = Column(String, nullable=True)
    fecha_eliminado = Column(DateTime(timezone=True), server_default=func.now())

