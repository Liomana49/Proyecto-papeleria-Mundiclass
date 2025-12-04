Mundiclass — Sistema de Inventario y Ventas (Proyecto)

Mundiclass es una aplicación web para la gestión de una papelería. Permite inventariar productos, administrar categorías, registrar clientes y gestionar ventas. Incluye una interfaz web con plantillas (Jinja2), un backend REST (FastAPI) y utilidades para generar gráficas y reportes a partir de los datos.

Este proyecto fue realizado como trabajo para la materia Desarrollo de Software.

Creadora: Laura Omaña Berrio
Profesor: Sergio Iván Galvis Mota

Características principales

- CRUD de Categorías, Productos, Clientes y Ventas.
- Control de inventario y actualización automática al registrar ventas.
- Validaciones de negocio (por ejemplo, código de categoría único).
- Historial de eliminaciones/ediciones para trazabilidad.
- Página de gráficas (Chart.js) con visualizaciones: productos por categoría, ventas por mes, top clientes, valor de inventario, etc.
- Plantillas HTML responsivas y menú lateral para navegación.

Estructura del repositorio

- main.py — punto de entrada de la aplicación (FastAPI + rutas para páginas y API).
- crud.py — lógica de acceso a datos y reglas de negocio.
- models.py / schemas.py — modelos ORM y esquemas Pydantic.
- templates/ — plantillas Jinja2 para la interfaz (incluye graficas.html, planning.html, index.html, etc.).
- static/ — archivos estáticos (CSS, JS, imágenes).
- datos.sql — script SQL con esquema y datos de ejemplo usados para las gráficas y pruebas.
- requirements.txt — dependencias Python.

Tecnologías

- Python (3.8+ recomendado)
- FastAPI
- SQLAlchemy (async) / AsyncSession
- Jinja2
- Chart.js (en frontend para gráficos)

Instalación (Windows — PowerShell)

1. Crear y activar entorno virtual (si no existe):

    python -m venv myvenv
    .\myvenv\Scripts\Activate.ps1

2. Instalar dependencias:

    pip install -r requirements.txt

3. (Opcional) Cargar datos de ejemplo desde datos.sql en tu motor de BD preferido.

Ejecutar la aplicación (desarrollo)

    .\myvenv\Scripts\Activate.ps1
    uvicorn main:app --reload --port 8000

Después abre http://127.0.0.1:8000 en tu navegador.

graficas.html y datos.sql

La página de gráficas (/graficas) está incluida en templates/graficas.html. En la versión actual del proyecto las gráficas pueden usar datos embebidos que coinciden con el contenido de datos.sql. Si prefieres que las gráficas usen datos en tiempo real, adapta la plantilla para hacer fetch contra los endpoints API (/api/productos, /api/compras, /api/clientes, /api/categorias).

Buenas prácticas y notas

- Reinicia el servidor después de cambiar rutas, plantillas o el archivo main.py.
- Si trabajas con una base de datos distinta a la usada por defecto, ajusta la URL de conexión en database.py.
- Mantén respaldos de la base de datos antes de ejecutar scripts de inserción o eliminación masiva.

Extensiones sugeridas

- Autenticación y roles (administrador, cajero).
- Exportación de reportes (CSV, PDF).
- Alertas por stock bajo y pedidos automáticos.
- Integración con servicios de facturación y pagos.

Licencia

Este repositorio incluye código de ejemplo para fines educativos. Añade la licencia que prefieras (por ejemplo, MIT) si deseas compartirlo públicamente.

Si quieres, puedo adaptar este README para incluir instrucciones específicas según la base de datos que uses (Postgres/SQLite) o agregar comandos para Docker.
