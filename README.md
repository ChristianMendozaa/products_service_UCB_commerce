# Products Service - UCB Commerce

Microservicio responsable de la gestión del catálogo de productos de la plataforma.

## Descripción

Este servicio permite la administración completa de los productos (CRUD), incluyendo su categorización, asignación a carreras y control de inventario básico. Sirve como la fuente de verdad para la información de los productos mostrada en el frontend y utilizada por el servicio de órdenes.

## Tecnologías

- **Lenguaje:** Python 3.10+
- **Framework:** FastAPI
- **Base de Datos:** Google Firestore (NoSQL)

## Funcionalidades Principales

- **Gestión de Productos:**
  - Crear, leer, actualizar y eliminar productos.
  - Soporte para imágenes (URLs o integración con servicio de imágenes).
- **Filtrado y Búsqueda:**
  - Listado de productos con filtros por categoría y carrera.
  - Paginación de resultados.
- **Control de Acceso:**
  - Solo administradores (de carrera o plataforma) pueden crear, editar o eliminar productos.
  - Lectura pública (o restringida a usuarios autenticados) del catálogo.

## Estructura del Proyecto

```
app/
├── core/           # Configuración y conexión a BD
├── deps/           # Dependencias de autenticación
├── repositories/   # Capa de acceso a datos (Firestore)
├── routers/        # Endpoints de la API (products)
├── schemas/        # Modelos de datos (Product, ProductCreate)
└── services/       # Lógica de negocio
```

## Instalación y Ejecución

1.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
# Products Service - UCB Commerce

Microservicio responsable de la gestión del catálogo de productos de la plataforma.

## Descripción

Este servicio permite la administración completa de los productos (CRUD), incluyendo su categorización, asignación a carreras y control de inventario básico. Sirve como la fuente de verdad para la información de los productos mostrada en el frontend y utilizada por el servicio de órdenes.

## Tecnologías

- **Lenguaje:** Python 3.10+
- **Framework:** FastAPI
- **Base de Datos:** Google Firestore (NoSQL)

## Funcionalidades Principales

- **Gestión de Productos:**
  - Crear, leer, actualizar y eliminar productos.
  - Soporte para imágenes (URLs o integración con servicio de imágenes).
- **Filtrado y Búsqueda:**
  - Listado de productos con filtros por categoría y carrera.
  - Paginación de resultados.
- **Control de Acceso:**
  - Solo administradores (de carrera o plataforma) pueden crear, editar o eliminar productos.
  - Lectura pública (o restringida a usuarios autenticados) del catálogo.

## Estructura del Proyecto

```
app/
├── core/           # Configuración y conexión a BD
├── deps/           # Dependencias de autenticación
├── repositories/   # Capa de acceso a datos (Firestore)
├── routers/        # Endpoints de la API (products)
├── schemas/        # Modelos de datos (Product, ProductCreate)
└── services/       # Lógica de negocio
```

## Instalación y Ejecución

1.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configurar variables de entorno:**
    Configurar `.env` con credenciales de Firebase.

3.  **Ejecutar el servidor:**
    ```bash
    uvicorn app.main:app --reload --port 8003
    ```

## Integración RAG (Chatbot)

Este servicio sincroniza automáticamente los cambios en los productos con una base de datos vectorial en Supabase para alimentar el sistema RAG del chatbot.

### Configuración RAG

Variables de entorno requeridas en `.env`:
- `OPENAI_API_KEY`: Para generar embeddings.
- `SUPABASE_URL`: URL del proyecto Supabase.
- `SUPABASE_SERVICE_ROLE_KEY`: Key con permisos de escritura (Service Role) para actualizar la tabla `rag_ucbcommerce_chunks`.

### Sincronización

- **Automática**: Al crear, actualizar o eliminar un producto, se actualiza su "ficha" en Supabase.
- **Manual (Force Sync)**: Endpoint administrativo para regenerar embeddings de TODOS los productos.
  - `POST /api/products/force-rag-sync`