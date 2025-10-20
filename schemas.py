from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------------- USUARIO ----------------
class UsuarioBase(BaseModel):
    nombre: str
    correo: str
    cedula: str
    tipo: str
    cliente_frecuente: Optional[bool] = False

class UsuarioCreate(UsuarioBase): pass
class UsuarioUpdate(UsuarioBase): pass

class UsuarioRead(UsuarioBase):
    id: int
    class Config: orm_mode = True

# ---------------- CLIENTE ----------------
class ClienteBase(BaseModel):
    nombre: str
    cedula: str
    activo: Optional[bool] = True

class ClienteCreate(ClienteBase): pass
class ClienteUpdate(ClienteBase): pass

class ClienteRead(ClienteBase):
    id: int
    class Config: orm_mode = True

# ---------------- CATEGORIA ----------------
class CategoriaBase(BaseModel):
    nombre: str
    codigo: Optional[str] = None

class CategoriaCreate(CategoriaBase): pass
class CategoriaUpdate(CategoriaBase): pass

class CategoriaRead(CategoriaBase):
    id: int
    class Config: orm_mode = True

# ---------------- PRODUCTO ----------------
class ProductoBase(BaseModel):
    nombre: str
    stock: int
    valor_unitario: float
    valor_unitario_mayor: Optional[float] = None
    umbral_mayor: Optional[int] = 20
    categoria_id: Optional[int] = None

class ProductoCreate(ProductoBase): pass
class ProductoUpdate(ProductoBase): pass

class ProductoRead(ProductoBase):
    id: int
    class Config: orm_mode = True

# ---------------- COMPRA ----------------
class CompraBase(BaseModel):
    cliente_id: int
    producto_id: int
    cantidad: int

class CompraCreate(CompraBase): pass

class CompraRead(CompraBase):
    id: int
    fecha: datetime
    class Config: orm_mode = True

# ---------------- HISTORIAL ----------------
class HistorialRead(BaseModel):
    id: int
    tabla: str
    registro_id: int
    descripcion: Optional[str]
    fecha_eliminado: datetime
    class Config: orm_mode = True
