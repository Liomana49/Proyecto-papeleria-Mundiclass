
from sqlalchemy import Column, Integer, String, Enum as SAEnum
from enum import Enum
from database import Base

class RolUsuario(str, Enum):
    administrador = "administrador"
    vendedor = "vendedor"
    proveedor = "proveedor"
    cliente = "cliente"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    rol = Column(SAEnum(RolUsuario), nullable=False, default=RolUsuario.vendedor)
    