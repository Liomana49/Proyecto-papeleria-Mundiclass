from typing import List, Optional
from datetime import datetime
import os
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    Response,
    UploadFile,
    File,
)
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Categoria, HistorialEliminados
import schemas

router = APIRouter(prefix="/categorias", tags=["Categorias"])


async def log_delete(
    db: AsyncSession,
    tabla: str,
    registro_id: int,
    descripcion: str | None = None,
):
    h = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos={
            "descripcion": descripcion or "",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
    db.add(h)


@router.get("/", response_model=List[schemas.CategoriaRead])
async def listar_categorias(
    nombre: Optional[str] = Query(None),
    codigo: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Categoria)
    conds = []
    if nombre:
        conds.append(Categoria.nombre == nombre)
    if codigo:
        conds.append(Categoria.codigo == codigo)
    if conds:
        stmt = stmt.where(and_(*conds))
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post(
    "/",
    response_model=schemas.CategoriaRead,
    status_code=status.HTTP_201_CREATED,
)
async def crear_categoria(
    payload: schemas.CategoriaCreate,
    db: AsyncSession = Depends(get_db),
):
    obj = Categoria(**payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/{categoria_id}", response_model=schemas.CategoriaRead)
async def actualizar_categoria(
    categoria_id: int,
    payload: schemas.CategoriaUpdate,
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    await log_delete(db, "Categoria", obj.id, f"Categoría '{obj.nombre}' eliminada")
    await db.delete(obj)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/historial/eliminados",
    response_model=List[schemas.HistorialEliminadoRead],
)
async def historial_categorias_eliminadas(
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Categoria")
        .order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()


# ==========================
#   SUBIR IMAGEN CATEGORÍA
# ==========================
@router.post("/{categoria_id}/imagen")
async def subir_imagen_categoria(
    categoria_id: int,
    archivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # 1) Verificar que la categoría exista
    res = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
    categoria = res.scalar_one_or_none()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # 2) Validar que el archivo sea imagen
    if not archivo.content_type or not archivo.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen (jpg, png, etc.)",
        )

    # 3) Carpeta donde se guardan las imágenes
    carpeta = "static/categorias"
    os.makedirs(carpeta, exist_ok=True)

    # 4) Construir nombre de archivo único
    extension = os.path.splitext(archivo.filename or "")[1] or ".jpg"
    nombre_archivo = f"cat_{categoria_id}_{uuid4().hex}{extension}"
    ruta_fisica = os.path.join(carpeta, nombre_archivo)

    # 5) Guardar archivo en disco
    contenido = await archivo.read()
    with open(ruta_fisica, "wb") as f:
        f.write(contenido)

    # 6) URL pública (asumiendo que montas /static en main.py)
    url_publica = f"/static/categorias/{nombre_archivo}"

    # Si luego agregas un campo imagen_url en Categoria, aquí lo podrías guardar:
    # categoria.imagen_url = url_publica
    # await db.commit()
    # await db.refresh(categoria)

    return {
        "categoria_id": categoria_id,
        "filename": nombre_archivo,
        "imagen_url": url_publica,
    }

