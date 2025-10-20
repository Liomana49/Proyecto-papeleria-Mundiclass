from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from database import Base

# -----------------------------
# MODELO: USUARIO
# -----------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    contraseña = Column(String(120), nullable=False)  # si prefieres evita la ñ y usa 'contrasena'
    rol = Column(String(50), nullable=False)  # administrador o cliente
    cedula = Column(String(20), unique=True, nullable=True, index=True)

    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    clientes = relationship("Cliente", back_populates="usuario")

# -----------------------------
# MODELO: CLIENTE
# -----------------------------
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    tipo_cliente = Column(String(20), nullable=False)            # mayorista o minorista
    cliente_frecuente = Column(String(10), nullable=False, default="no")  # "si" / "no"
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("Usuario", back_populates="clientes")
    compras = relationship("Compra", back_populates="cliente")

# -----------------------------
# MODELO: CATEGORIA
# -----------------------------
class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(120), nullable=False, index=True)
    codigo = Column(String(30), nullable=True, index=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    actualizado_en = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    productos = relationship("Producto", back_populates="categoria")

# -----------------------------
# MODELO: PRODUCTO
# -----------------------------
class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(120), nullable=False, index=True)
    descripcion = Column(String(250))
    cantidad = Column(Integer, nullable=False, default=0)
    valor_unitario = Column(Float, nullable=False)
    valor_mayorista = Column(Float, nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    categoria = relationship("Categoria", back_populates="productos")
    compras = relationship("Compra", back_populates="producto")

# -----------------------------
# MODELO: COMPRA
# -----------------------------
class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cliente = relationship("Cliente", back_populates="compras")
    producto = relationship("Producto", back_populates="compras")

# -----------------------------
# HISTORIAL DE ELIMINADOS
# -----------------------------
class HistorialEliminados(Base):
    __tablename__ = "historial_eliminados"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tabla = Column(String(50), nullable=False)
    registro_id = Column(Integer, nullable=False)
    datos = Column(JSONB, nullable=False, default=dict)  # snapshot en JSONB
    eliminado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)





