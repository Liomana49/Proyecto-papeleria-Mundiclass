# models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    func,
    and_,
)
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


# -----------------------------
# MODELO: MULTIMEDIA
# -----------------------------
class Multimedia(Base):
    __tablename__ = "multimedia"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    media_type = Column(String(50), nullable=False)  # image, video, audio, etc.
    description = Column(String(255), nullable=True)

    model_type = Column(String(50), nullable=False)  # Which model owns this multimedia: Usuario, Cliente, etc.
    model_id = Column(Integer, nullable=False)  # The primary key of the owning model instance

    creado_en = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    actualizado_en = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# -----------------------------
# MODELO: USUARIO
# -----------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    # usa 'contrasena' para evitar problemas con la ñ en JSON/código
    contrasena = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False)  # administrador / cliente

    # Datos comerciales
    cedula = Column(String(20), unique=True, nullable=False)
    tipo = Column(String(20), nullable=True)  # mayorista / minorista
    cliente_frecuente = Column(Boolean, nullable=False, default=False)

    creado_en = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    actualizado_en = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relaciones
    clientes = relationship("Cliente", back_populates="usuario")
    multimedia = relationship(
        "Multimedia",
        primaryjoin="and_(foreign(Multimedia.model_id)==Usuario.id, Multimedia.model_type=='Usuario')",
        viewonly=True,
    )


# -----------------------------
# MODELO: CLIENTE
# -----------------------------
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)

    tipo_cliente = Column(String(20), nullable=True)  # mayorista / minorista
    cliente_frecuente = Column(Boolean, nullable=False, default=False)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    creado_en = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relaciones
    usuario = relationship("Usuario", back_populates="clientes")
    compras = relationship("Compra", back_populates="cliente")
    multimedia = relationship(
        "Multimedia",
        primaryjoin="and_(foreign(Multimedia.model_id)==Cliente.id, Multimedia.model_type=='Cliente')",
        viewonly=True,
    )


# -----------------------------
# MODELO: CATEGORIA
# -----------------------------
class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(120), nullable=False, index=True)
    codigo = Column(String(30), nullable=True, index=True)

    # 👇 NUEVO: URL de la imagen asociada a la categoría
    imagen_url = Column(String(255), nullable=True)

    creado_en = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    actualizado_en = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relaciones
    productos = relationship("Producto", back_populates="categoria")
    multimedia = relationship(
        "Multimedia",
        primaryjoin="and_(foreign(Multimedia.model_id)==Categoria.id, Multimedia.model_type=='Categoria')",
        viewonly=True,
    )


# -----------------------------
# MODELO: PRODUCTO
# -----------------------------
class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(120), nullable=False, index=True)
    descripcion = Column(String(250), nullable=True)

    cantidad = Column(Integer, nullable=False, default=0)
    valor_unitario = Column(Float, nullable=False)
    valor_mayorista = Column(Float, nullable=True)

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)

    # 👇 NUEVO: URL de la imagen asociada al producto
    imagen_url = Column(String(255), nullable=True)

    creado_en = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    actualizado_en = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    compras = relationship("Compra", back_populates="producto")
    multimedia = relationship(
        "Multimedia",
        primaryjoin="and_(foreign(Multimedia.model_id)==Producto.id, Multimedia.model_type=='Producto')",
        viewonly=True,
    )


# -----------------------------
# MODELO: COMPRA
# -----------------------------
class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)

    cantidad = Column(Integer, nullable=False, default=1)

    # Precio que realmente se aplicó (unitario) y total
    precio_unitario_aplicado = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    fecha = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relaciones
    cliente = relationship("Cliente", back_populates="compras")
    producto = relationship("Producto", back_populates="compras")
    multimedia = relationship(
        "Multimedia",
        primaryjoin="and_(foreign(Multimedia.model_id)==Compra.id, Multimedia.model_type=='Compra')",
        viewonly=True,
    )


# -----------------------------
# HISTORIAL DE ELIMINADOS
# -----------------------------
class HistorialEliminados(Base):
    __tablename__ = "historial_eliminados"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # nombre de la tabla afectada (usuarios, productos, etc.)
    tabla = Column(String(50), nullable=False)
    # id del registro eliminado en esa tabla
    registro_id = Column(Integer, nullable=False)
    # snapshot en JSONB (Postgres lo soporta sin problema)
    datos = Column(JSONB, nullable=False, default=dict)

    eliminado_en = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
