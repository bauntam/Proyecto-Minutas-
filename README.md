# MVP Minutas por Jardín (Tkinter + SQLite)

Aplicación de escritorio simple para crear y gestionar **jardines**, **minutas** e **ingredientes en gramos**.
Está pensada para una primera entrega usable y estable.

## Funcionalidades incluidas

- **Catálogo de alimentos**
  - Carga inicial automática al primer arranque.
  - Alta de nuevos alimentos desde interfaz.
  - Evita duplicados por nombre (sin importar mayúsculas/minúsculas ni espacios extra).
- **Jardines**
  - Crear, listar, renombrar y eliminar.
- **Minutas por jardín**
  - Crear minuta dentro de un jardín.
  - Agregar ingredientes desde catálogo con cantidad en gramos (> 0).
  - Editar gramos y quitar ingredientes.
  - Listar y abrir minutas para edición.
- **Persistencia local**
  - SQLite en `data/minutas.db`.
  - Los datos se conservan al cerrar y volver a abrir la app.

## Estructura del proyecto

```text
src/
  app.py           # Entrada principal
  db.py            # SQLite + creación de tablas
  models.py        # Operaciones CRUD + validaciones
  ui_main.py       # Pantalla principal
  ui_catalogo.py   # Gestión de alimentos
  ui_jardines.py   # Gestión de jardines
  ui_minutas.py    # Editor de minutas e ingredientes
  seed.py          # Catálogo inicial
requirements.txt
README.md
```

## Base de datos

Tablas:

- `alimentos(id, nombre UNIQUE)`
- `jardines(id, nombre UNIQUE)`
- `minutas(id, jardin_id, nombre, fecha_creacion)`
- `minuta_items(id, minuta_id, alimento_id, gramos)`

## Ejecución en Windows 11

1. Abrir una terminal (PowerShell o CMD) en la carpeta del proyecto.
2. Crear entorno virtual:

```powershell
python -m venv .venv
```

3. Activar entorno virtual:

```powershell
.venv\Scripts\activate
```

4. Ejecutar aplicación:

```powershell
python src\app.py
```

## Cómo probar (checklist)

1. Abrir app.
2. Entrar a **Gestionar Jardines**:
   - crear 2 jardines,
   - renombrar uno,
   - eliminar uno.
3. Entrar a **Gestionar Catálogo**:
   - verificar alimentos precargados,
   - crear un alimento nuevo,
   - intentar crear duplicado (debe mostrar mensaje).
4. En pantalla principal:
   - seleccionar jardín,
   - crear minuta,
   - abrir minuta,
   - agregar ingredientes con gramos,
   - editar gramos,
   - quitar ingrediente.
5. Cerrar y volver a abrir app:
   - confirmar que jardines/minutas/ingredientes siguen guardados.

## Seed del catálogo inicial

- El seed se ejecuta automáticamente en el inicio si `alimentos` está vacío.
- También se puede ejecutar manualmente:

```powershell
python src\seed.py
```
