from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB  # 👈 importante
from database import Base

# -----------------------------
# MODELO: USUARIO
# -----------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    contraseña = Column(String(120), nullable=False)
    rol = Column(String(50), nullable=False)  # administrador o cliente

    # 👇 agregado para que el router no falle (puede ser opcional para admin)
    cedula = Column(String(20), unique=True, nullable=True, index=True)

    creado_en = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)

    clientes = relationship("Cliente", back_populates="usuario")


# -----------------------------
# MODELO: CLIENTE
# -----------------------------
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    tipo_cliente = Column(String(20), nullable=False)  # mayorista o minorista
    cliente_frecuente = Column(String(10), nullable=False, default="no")  # sí o no
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    creado_en = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)

    # 🔧 ESTA LÍNEA ES LA CORRECTA
    usuario = relationship("Usuario", back_populates="clientes")
    compras = relationship("Compra", back_populates="cliente")




