# models.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Numeric, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base  # <- tu Base declarativa


# ----------------------------
# USUARIO  (mayorista/minorista, cédula, cliente_frecuente)
# ----------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    cedula: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    # 'mayorista' o 'minorista'
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    cliente_frecuente: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # 1:1 con Cliente (opcional: un usuario puede tener un perfil de cliente)
    cliente: Mapped["Cliente"] = relationship(
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan"
    )

    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint("tipo IN ('mayorista','minorista')", name="ck_usuarios_tipo_valido"),
        Index("ix_usuarios_tipo_frecuente", "tipo", "cliente_frecuente"),
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} cedula={self.cedula} tipo={self.tipo} frecuente={self.cliente_frecuente}>"


# ----------------------------
# CATEGORIA  (con 'codigo' y 'nombre')
# ----------------------------
class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # código interno
    codigo: Mapped[str | None] = mapped_column(String(30), unique=True, index=True)  # código visible (opcional)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    productos: Mapped[list["Producto"]] = relationship("Producto", back_populates="categoria")

    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("codigo", name="uq_categorias_codigo"),
        Index("ix_categorias_nombre", "nombre"),
    )

    def __repr__(self) -> str:
        return f"<Categoria id={self.id} codigo={self.codigo} nombre={self.nombre}>"


# ----------------------------
# PRODUCTO  (valor_unitario, valor_unitario_mayor, umbral_mayor, filtros por nombre/stock)
# ----------------------------
class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)

    # Precios
    valor_unitario: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    valor_unitario_mayor: Mapped[Numeric | None] = mapped_column(Numeric(10, 2), nullable=True)
    umbral_mayor: Mapped[int] = mapped_column(Integer, default=20, nullable=False)

    # Estado
    activo: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # FK a Categoria (opcional si usas categorías)
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"), nullable=True)
    categoria: Mapped[Categoria | None] = relationship("Categoria", back_populates="productos")

    # N:N con Compra a través de DetalleCompra
    items: Mapped[list["DetalleCompra"]] = relationship("DetalleCompra", back_populates="producto")

    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_productos_stock_no_negativo"),
        CheckConstraint("umbral_mayor >= 0", name="ck_productos_umbral_no_negativo"),
        Index("ix_productos_nombre_stock", "nombre", "stock"),
    )

    def __repr__(self) -> str:
        return f"<Producto id={self.id} nombre={self.nombre} stock={self.stock}>"


# ----------------------------
# CLIENTE  (perfil 1:1 del Usuario)
# ----------------------------
class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Relación 1:1 -> cada Cliente corresponde a un Usuario
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), unique=True, nullable=False, index=True)
    usuario: Mapped[Usuario] = relationship("Usuario", back_populates="cliente", uselist=False)

    # Datos propios del cliente (opcional)
    telefono: Mapped[str | None] = mapped_column(String(30))
    direccion: Mapped[str | None] = mapped_column(String(200))
    activo: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # 1:N -> Cliente tiene muchas Compras
    compras: Mapped[list["Compra"]] = relationship("Compra", back_populates="cliente", cascade="all, delete")

    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Cliente id={self.id} usuario_id={self.usuario_id} activo={self.activo}>"


# ----------------------------
# COMPRA  (cabecera)
# ----------------------------
class Compra(Base):
    __tablename__ = "compras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False, index=True)
    cliente: Mapped[Cliente] = relationship("Cliente", back_populates="compras")

    # N:N con Producto vía DetalleCompra
    items: Mapped[list["DetalleCompra"]] = relationship(
        "DetalleCompra", back_populates="compra", cascade="all, delete-orphan"
    )

    # Totales opcionales (puedes calcularlos en servicios)
    subtotal: Mapped[Numeric | None] = mapped_column(Numeric(12, 2))
    total: Mapped[Numeric | None] = mapped_column(Numeric(12, 2))

    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Compra id={self.id} cliente_id={self.cliente_id}>"


# ----------------------------
# DETALLE_COMPRA  (tabla puente N:N con precio aplicado y cantidad)
# ----------------------------
class DetalleCompra(Base):
    __tablename__ = "detalles_compra"

    compra_id: Mapped[int] = mapped_column(ForeignKey("compras.id"), primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), primary_key=True)

    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    # precio_unitario_aplicado = el valor que se usó en el momento de la compra
    precio_unitario_aplicado: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)

    compra: Mapped[Compra] = relationship("Compra", back_populates="items")
    producto: Mapped[Producto] = relationship("Producto", back_populates="items")

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_detalle_cantidad_positiva"),
    )

    def __repr__(self) -> str:
        return f"<DetalleCompra compra={self.compra_id} producto={self.producto_id} cant={self.cantidad}>"
