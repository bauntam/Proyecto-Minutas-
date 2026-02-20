# Proyecto Minutas por Jardín

Aplicación de escritorio (MVP) para gestionar minutas de alimentación por jardín infantil. El proyecto mantiene una arquitectura por capas para facilitar su crecimiento a módulos como exportación, pedidos automáticos, cálculo nutricional y una eventual versión web.

## Funcionalidades del MVP

- **Catálogo de alimentos**
  - Seed inicial automático al primer inicio.
  - Alta de alimentos desde interfaz.
- **Jardines**
  - Alta y listado de jardines.
- **Minutas**
  - Creación de minutas por jardín.
  - Agregado de ingredientes por minuta con cantidades en gramos.
- **Persistencia local**
  - SQLite en `data/minutas.db`.
  - Conserva datos entre ejecuciones.

## Arquitectura (separación de capas)

```text
src/
  main.py                # Punto de entrada
  database/              # Capa de datos (SQLite)
    connection.py
    schema.py
    seed.py
  models/                # Entidades del dominio
    entities.py
  services/              # Lógica de negocio
    garden_service.py
    food_service.py
    minute_service.py
  ui/                    # Interfaz gráfica (Tkinter)
    app.py
app.py                   # Wrapper de compatibilidad para ejecutar desde raíz
```

### 1) Capa de datos
- `database/connection.py` encapsula conexión y operaciones SQLite.
- `database/schema.py` define tablas y restricciones.
- `database/seed.py` carga catálogo inicial de alimentos.

### 2) Capa de negocio
- `services/` contiene reglas y validaciones (ej. nombre obligatorio, gramos > 0).
- La UI no consulta SQL directo: consume servicios.

### 3) Capa de interfaz
- `ui/app.py` implementa interfaz mínima en Tkinter.
- Se enfoca en captura/interacción y delega operaciones a la capa de negocio.

## Modelo relacional

Tablas incluidas:

- `jardines`
- `minutas`
- `alimentos`
- `minuta_items`

Relaciones:
- Un jardín tiene muchas minutas (`minutas.jardin_id`).
- Una minuta tiene muchos ingredientes (`minuta_items.minuta_id`).
- Cada ingrediente referencia un alimento del catálogo (`minuta_items.alimento_id`).

## Requisitos

- Windows 11 (o Linux/macOS con Tkinter disponible).
- Python 3.10+.

## Ejecución en Windows 11

1. Abrir PowerShell y moverse al proyecto:

```powershell
cd C:\ruta\a\Proyecto-Minutas-
```

2. (Opcional recomendado) Crear entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Ejecutar la aplicación:

```powershell
python app.py
```

También puedes ejecutarla con:

```powershell
python src\main.py
```

## Datos y seed inicial

- La base de datos se crea automáticamente en `data/minutas.db` al primer inicio.
- El catálogo inicial se inserta automáticamente si la tabla está vacía y no duplica registros.

## Roadmap técnico (siguientes pasos sugeridos)

1. Agregar pruebas unitarias para `services/`.
2. Incorporar repositorios (`repositories/`) para mayor desacople SQL.
3. Definir casos de uso formales (application layer).
4. Añadir migraciones versionadas.
