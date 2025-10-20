# schemas.py (Pydantic v2)
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

# ---------------- USUARIO ----------------
class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    rol: str                       # "administrador" / "cliente"
    cedula: Optional[str] = None   # en modelo es nullable=True

class UsuarioCreate(UsuarioBase):
    # usa 'contrasena' si prefieres evitar la ñ en JSON; tu modelo es 'contraseña'
    contraseña: str

class UsuarioUpdate(BaseModel):
    # todo opcional para updates parciales
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    rol: Optional[str] = None
    cedula: Optional[str] = None
    contraseña: Optional[str] = None

class UsuarioRead(UsuarioBase):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)

# ---------------- CLIENTE ----------------
class ClienteBase(BaseModel):
    nombre: str
    cedula: str
    tipo_cliente: str                   # "mayorista" / "minorista"
    cliente_frecuente: str = "no"       # "si" / "no"
    usuario_id: Optional[int] = None    # FK opcional según tu modelo

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    cedula: Optional[str] = None
    tipo_cliente: Optional[str] = None
    cliente_frecuente: Optional[str] = None
    usuario_id: Optional[int] = None

class ClienteRead(ClienteBase):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)

# ---------------- CATEGORIA ----------------
class CategoriaBase(BaseModel):
    nombre: str
    codigo: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None

class CategoriaRead(CategoriaBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)

# ---------------- PRODUCTO ----------------
class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    cantidad: int
    valor_unitario: float
    valor_mayorista: Optional[float] = None
    categoria_id: Optional[int] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    cantidad: Optional[int] = None
    valor_unitario: Optional[float] = None
    valor_mayorista: Optional[float] = None
    categoria_id: Optional[int] = None

class ProductoRead(ProductoBase):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)

# ---------------- COMPRA ----------------
class CompraBase(BaseModel):
    cliente_id: int
    producto_id: int
    cantidad: int
    total: float

class CompraCreate(CompraBase):
    pass

class CompraRead(CompraBase):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)

# ---------------- HISTORIAL ----------------
class HistorialEliminadoRead(BaseModel):
    id: int
    tabla: str
    registro_id: int
    datos: dict                    # JSONB -> dict
    eliminado_en: datetime
    model_config = ConfigDict(from_attributes=True)
