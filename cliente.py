from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from enum import Enum
from database import Base

class TipoCliente(str, Enum):
    mayorista = "mayorista"
    minorista = "minorista"

class Cliente(Base):
    __tablename__ = "clientes"
    __table_args__ = (
        UniqueConstraint("cedula", name="uq_clientes_cedula"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    cedula = Column(String(30), nullable=False, index=True)  # <-- agregado
    tipo = Column(SAEnum(TipoCliente), nullable=False, default=TipoCliente.minorista)
    es_potencial = Column(Boolean, default=False)
    frecuencia_compra_dias = Column(Integer, nullable=True)

    compras = relationship("Compra", back_populates="cliente")
