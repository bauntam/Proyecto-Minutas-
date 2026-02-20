# MVP Minutas por Jardín (Tkinter + SQLite)

Aplicación de escritorio sencilla para crear y gestionar minutas por jardín infantil.

## Funcionalidades del MVP

- **Catálogo de alimentos**
  - Carga inicial automática de alimentos al primer inicio.
  - Alta de nuevos alimentos desde interfaz.
  - Validación de duplicados por nombre (sin distinguir mayúsculas/minúsculas y espacios extra).
- **Jardines**
  - Crear, listar, renombrar y eliminar.
- **Minutas**
  - Crear minutas dentro de un jardín.
  - Agregar ingredientes del catálogo con gramos.
  - Editar gramos y quitar ingredientes.
- **Persistencia local**
  - SQLite en `data/minutas.db`.
  - Conserva datos al cerrar y abrir.

## Estructura del proyecto

```text
/src
  app.py
  db.py
  models.py
  ui_main.py
  ui_catalogo.py
  ui_jardines.py
  ui_minutas.py
  seed.py
/tests
README.md
requirements.txt
```

## Requisitos

- Windows 11
- Python 3.10+ (incluye Tkinter por defecto)

## Ejecución (Windows 11)

1. Abrir terminal en la carpeta del proyecto.
2. Crear entorno virtual:

```bat
python -m venv .venv
```

3. Activar entorno virtual:

```bat
.venv\Scripts\activate
```

4. Ejecutar la aplicación:

```bat
python src\app.py
```

## Script/función para catálogo inicial

- El catálogo inicial está en `src/seed.py` (`INITIAL_FOODS`).
- La función `seed_if_empty(conn)` inserta los alimentos **solo si** la tabla está vacía.
- Se ejecuta automáticamente al iniciar la app desde `src/app.py`.

## Cómo probar rápidamente

1. Ejecuta la app.
2. Abre **Gestionar jardines** y crea un jardín.
3. Crea una **Nueva minuta**.
4. Abre la minuta y agrega ingredientes con gramos (> 0).
5. Edita gramos y elimina un ingrediente.
6. Cierra la app y vuelve a abrir: los datos deben seguir ahí.
