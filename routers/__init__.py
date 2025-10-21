from . import (
    router_usuario,
    router_cliente,
    router_producto,
    router_categoria,  # ✅ corregido (sin 's')
    router_compra,
    router_historial,  # 👈 correcto
)

__all__ = [
    "router_usuario",
    "router_cliente",
    "router_producto",
    "router_categoria",  # ✅ corregido
    "router_compra",
    "router_historial",  # 👈 correcto
]

