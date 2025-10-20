# routers/__init__.py

from . import (
    router_usuario,
    router_cliente,
    router_producto,
    router_categorias,   # ✅ en plural (así se llama tu archivo)
    router_compra,
    router_historial,    # ✅ si tienes el historial
)

__all__ = [
    "router_usuario",
    "router_cliente",
    "router_producto",
    "router_categorias",  # ✅ plural
    "router_compra",
    "router_historial",
]
