# schemas.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime


# -----------------------------
# MODELO: MULTIMEDIA
# -----------------------------
class MultimediaBase(BaseModel):
    url: str
    media_type: str  # image, video, audio, etc.
    description: Optional[str] = None


class MultimediaCreate(MultimediaBase):
    model_type: str
    model_id: int


class MultimediaUpdate(BaseModel):
    url: Optional[str] = None
    media_type: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[str] = None
    model_id: Optional[int] = None


class MultimediaRead(MultimediaBase):
    id: int
    model_type: str
    model_id: int
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================
# ------- USUARIO ----------
# ==========================
class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    rol: str                       # "administrador" / "cliente"
    cedula: str                    # única
    tipo: Optional[str] = None     # mayorista / minorista
    cliente_frecuente: bool = False


class UsuarioCreate(UsuarioBase):
    contrasena: str


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    rol: Optional[str] = None
    cedula: Optional[str] = None
    tipo: Optional[str] = None
    cliente_frecuente: Optional[bool] = None
    contrasena: Optional[str] = None


class UsuarioRead(UsuarioBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime
    multimedia: Optional[List[MultimediaRead]] = []

    model_config = ConfigDict(from_attributes=True)


# ==========================
# ------- CLIENTE ----------
# ==========================
class ClienteBase(BaseModel):
    nombre: str
    cedula: str
    tipo_cliente: Optional[str] = None    # mayorista / minorista
    cliente_frecuente: bool = False
    usuario_id: Optional[int] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    cedula: Optional[str] = None
    tipo_cliente: Optional[str] = None
    cliente_frecuente: Optional[bool] = None
    usuario_id: Optional[int] = None


class ClienteRead(ClienteBase):
    id: int
    creado_en: datetime
    multimedia: Optional[List[MultimediaRead]] = []

    model_config = ConfigDict(from_attributes=True)


# ==========================
# ------ CATEGORÍA ---------
# ==========================

class CategoriaBase(BaseModel):
    nombre: str
    codigo: Optional[str] = None
    imagen_url: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    imagen_url: Optional[str] = None


class CategoriaRead(CategoriaBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================
# ------- PRODUCTO ---------
# ==========================
class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    cantidad: int
    valor_unitario: float
    valor_mayorista: Optional[float] = None
    categoria_id: Optional[int] = None
    imagen_url: Optional[str] = None


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    cantidad: Optional[int] = None
    valor_unitario: Optional[float] = None
    valor_mayorista: Optional[float] = None
    categoria_id: Optional[int] = None
    imagen_url: Optional[str] = None


class ProductoRead(ProductoBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================
# -------- COMPRA ----------
# ==========================
class CompraBase(BaseModel):
    cliente_id: int
    producto_id: int
    cantidad: int
    precio_unitario_aplicado: float
    total: float


class CompraCreate(CompraBase):
    pass


class CompraUpdate(BaseModel):
    cliente_id: Optional[int] = None
    producto_id: Optional[int] = None
    cantidad: Optional[int] = None
    precio_unitario_aplicado: Optional[float] = None
    total: Optional[float] = None


class CompraRead(CompraBase):
    id: int
    fecha: datetime
    multimedia: Optional[List[MultimediaRead]] = []

    model_config = ConfigDict(from_attributes=True)


# ==========================
# ---- HISTORIAL DELETE ----
# ==========================
class HistorialEliminadoRead(BaseModel):
    id: int
    tabla: str
    registro_id: int
    datos: dict
    eliminado_en: datetime

    model_config = ConfigDict(from_attributes=True)
