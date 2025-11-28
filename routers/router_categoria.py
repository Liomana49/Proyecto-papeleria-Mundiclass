from typing import List, Optional

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
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import schemas
import crud
from utils import upload_image_to_supabase

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("/", response_model=List[schemas.CategoriaRead])
async def listar_categorias(
    nombre: Optional[str] = None,
    codigo: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    # Si tu crud.listar_categorias acepta filtros, pásalos; si no, solo db
    return await crud.listar_categorias(db)


@router.post(
    "/",
    response_model=schemas.CategoriaRead,
    status_code=status.HTTP_201_CREATED,
)
async def crear_categoria(
    nombre: str = Query(...),
    codigo: Optional[str] = Query(None),
    imagen: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    # Si hay imagen, la subimos a Supabase y obtenemos la URL pública
    url_publica: Optional[str] = None
    if imagen:
        if not imagen.content_type or not imagen.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser una imagen (jpg, png, etc.)",
            )
        # 👇 usamos folder="categorias"
        url_publica = await upload_image_to_supabase(imagen, folder="categorias")

    # Construimos el dict de datos para el schema
    data_dict = {"nombre": nombre}
    if codigo:
        data_dict["codigo"] = codigo
    if url_publica:
        data_dict["imagen_url"] = url_publica

    payload = schemas.CategoriaCreate(**data_dict)
    categoria = await crud.crear_categoria(db, payload)
    return categoria


@router.put("/{categoria_id}", response_model=schemas.CategoriaRead)
async def actualizar_categoria(
    categoria_id: int,
    nombre: Optional[str] = Query(None),
    codigo: Optional[str] = Query(None),
    imagen: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    imagen_url: Optional[str] = None
    if imagen:
        if not imagen.content_type or not imagen.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser una imagen (jpg, png, etc.)",
            )
        # 👇 nuevamente folder="categorias"
        imagen_url = await upload_image_to_supabase(imagen, folder="categorias")

    payload = schemas.CategoriaUpdate(nombre=nombre, codigo=codigo, imagen_url=imagen_url)
    categoria = await crud.actualizar_categoria(db, categoria_id, payload)
    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_db),
):
    categoria = await crud.obtener_categoria(db, categoria_id)

    await crud._registrar_eliminado(
        db,
        "categorias",
        categoria.id,
        {"nombre": categoria.nombre},
    )
    await crud.borrar_categoria(db, categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/historial/eliminados",
    response_model=List[schemas.HistorialEliminadoRead],
)
async def historial_categorias_eliminadas(
    db: AsyncSession = Depends(get_db),
):
    return await crud.listar_historial(db)


# ==========================
#   SUBIR IMAGEN CATEGORÍA
# ==========================
@router.post("/{categoria_id}/imagen")
async def subir_imagen_categoria(
    categoria_id: int,
    archivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    categoria = await crud.obtener_categoria(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if not archivo.content_type or not archivo.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen (jpg, png, etc.)",
        )

    # 👇 usamos nuevamente folder="categorias"; bucket ya es 'Mundiclass'
    url_publica = await upload_image_to_supabase(archivo, folder="categorias")

    # Si quieres guardar la imagen en la BD también desde este endpoint:
    # from schemas import CategoriaUpdate
    # payload = CategoriaUpdate(imagen_url=url_publica)
    # await crud.actualizar_categoria(db, categoria_id, payload)

    return {
        "categoria_id": categoria_id,
        "url_publica": url_publica,
    }

