from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    imagen_url = Column(String, nullable=True)
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=0)

    categoria = relationship("Categoria", back_populates="productos")
    compras = relationship("Compra", back_populates="producto")
