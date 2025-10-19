# schemas.py
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Literal

from pydantic import BaseModel, Field, ConfigDict, conint, validator


# =========================================================
# USUARIO
# =========================================================
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    cedula: str = Field(..., min_length=5, max_length=20)
    tipo: Literal["mayorista", "minorista"]
    cliente_frecuente: bool = False

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=120)
    tipo: Optional[Literal["mayorista", "minorista"]] = None
    cliente_frecuente: Optional[bool] = None

class UsuarioRead(UsuarioBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# CATEGORIA
# =========================================================
class CategoriaBase(BaseModel):
    # "codigo" puede ser None si no lo usas; si lo usas, será único
    codigo: Optional[str] = Field(None, max_length=30)
    nombre: str = Field(..., min_length=2, max_length=120)

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=30)
    nombre: Optional[str] = Field(None, min_length=2, max_length=120)

class CategoriaRead(CategoriaBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# PRODUCTO
# =========================================================
class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150)
    stock: conint(ge=0) = 0
    valor_unitario: Decimal = Field(..., gt=0)
    valor_unitario_mayor: Optional[Decimal] = Field(None, gt=0)
    umbral_mayor: conint(ge=0) = 20
    activo: bool = True
    categoria_id: Optional[int] = None

    @validator("valor_unitario_mayor")
    def mayor_debe_tener_sentido(cls, v, values):
        # si viene precio mayor y también viene valor_unitario, el mayor no debería ser más alto (opcional)
        vu = values.get("valor_unitario")
        if v is not None and vu is not None and v >= vu:
            # en muchos negocios el precio por mayor es menor. Si no quieres esta regla, bórrala.
            return v
        return v

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    stock: Optional[conint(ge=0)] = None
    valor_unitario: Optional[Decimal] = Field(None, gt=0)
    valor_unitario_mayor: Optional[Decimal] = Field(None, gt=0)
    umbral_mayor: Optional[conint(ge=0)] = None
    activo: Optional[bool] = None
    categoria_id: Optional[int] = None

class ProductoRead(ProductoBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# CLIENTE  (perfil 1:1 del Usuario)
# =========================================================
class ClienteBase(BaseModel):
    telefono: Optional[str] = Field(None, max_length=30)
    direccion: Optional[str] = Field(None, max_length=200)
    activo: bool = True

class ClienteCreate(ClienteBase):
    usuario_id: int  # enlaza al Usuario

class ClienteUpdate(BaseModel):
    telefono: Optional[str] = Field(None, max_length=30)
    direccion: Optional[str] = Field(None, max_length=200)
    activo: Optional[bool] = None

class ClienteRead(ClienteBase):
    id: int
    usuario_id: int
    # Si quieres devolver los datos del usuario embebidos, usa el siguiente campo:
    # usuario: Optional[UsuarioRead] = None
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# DETALLE COMPRA (ítems)
# =========================================================
class DetalleCompraBase(BaseModel):
    producto_id: int
    cantidad: conint(gt=0)
    # En creación, el backend puede calcular el precio aplicado; si lo quieres enviar manual, permite opcional
    precio_unitario_aplicado: Optional[Decimal] = Field(None, gt=0)

class DetalleCompraCreate(DetalleCompraBase):
    pass

class DetalleCompraRead(DetalleCompraBase):
    compra_id: int
    # precio_unitario_aplicado debe venir ya calculado al leer
    precio_unitario_aplicado: Decimal
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# COMPRA (cabecera + lista de ítems)
# =========================================================
class CompraBase(BaseModel):
    subtotal: Optional[Decimal] = Field(None, ge=0)
    total: Optional[Decimal] = Field(None, ge=0)

class CompraCreate(CompraBase):
    cliente_id: int
    items: List[DetalleCompraCreate]

class CompraRead(CompraBase):
    id: int
    cliente_id: int
    items: List[DetalleCompraRead]
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)
