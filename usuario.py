from sqlalchemy import Column, Integer, String, Enum as SAEnum, UniqueConstraint
from enum import Enum
from database import Base

class RolUsuario(str, Enum):
    administrador = "administrador"
    vendedor = "vendedor"
    proveedor = "proveedor"
    cliente = "cliente"

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        UniqueConstraint("cedula", name="uq_usuarios_cedula"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    cedula = Column(String(30), nullable=False, index=True)  # <-- agregado
    rol = Column(SAEnum(RolUsuario), nullable=False, default=RolUsuario.vendedor)
