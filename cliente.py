from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from enum import Enum
from database import Base


class TipoCliente(str, Enum):
    mayorista = "mayorista"
    minorista = "minorista"


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)


    tipo = Column(SAEnum(TipoCliente), nullable=False, default=TipoCliente.minorista)

    
    es_potencial = Column(Boolean, default=False)

    
    frecuencia_compra_dias = Column(Integer, nullable=True)

    
    compras = relationship("Compra", back_populates="cliente")