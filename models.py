from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    imagen_url = Column(String, nullable=True)

    productos = relationship("Producto", back_populates="categoria")
