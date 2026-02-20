# Proyecto Minutas por Jardín

Aplicación de escritorio (MVP) para gestionar minutas de alimentación por jardín infantil, con arquitectura preparada para crecer hacia módulos de exportación, pedidos automáticos, cálculo nutricional y eventual migración a una versión web.

## Objetivos del MVP

- Gestionar **múltiples jardines**.
- Gestionar **múltiples minutas por jardín**.
- Gestionar **múltiples ingredientes por minuta**.
- Registrar cantidades en **gramos** (`REAL` en SQLite).
- Mantener un **catálogo editable de alimentos**.

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
```

### 1) Capa de datos
- `database/connection.py` encapsula conexión y operaciones SQLite.
- `database/schema.py` define tablas y restricciones.
- `database/seed.py` carga catálogo inicial de alimentos.

### 2) Capa de negocio
- `services/` contiene reglas y validaciones (ej. nombre obligatorio, gramos > 0).
- La UI no consulta SQL directo, consume servicios.

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

## Roadmap técnico (preparado para crecimiento)

- **Exportación a Excel**: se puede agregar servicio `export_service.py` sin acoplar UI/DB.
- **Generación automática de pedidos**: nuevo módulo en `services/` sobre agregación por rango de fechas/jardín.
- **Cálculo nutricional**: extensión de `alimentos` con macros/micronutrientes.
- **Versión web**: reutilizar `services/` y `models/` con API (FastAPI/Django/Flask).

## Requisitos

- Python 3.11+ (funciona también con 3.10 si soporta `|` en type hints).
- Tkinter disponible (incluido en la instalación estándar de Python para Windows).

## Ejecución en Windows 11

1. Instalar Python desde https://www.python.org/downloads/windows/  
   Durante la instalación, marcar **"Add Python to PATH"**.

2. Abrir **PowerShell** y moverse al proyecto:

```powershell
cd C:\ruta\a\Proyecto-Minutas-
```

3. (Opcional recomendado) Crear entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Ejecutar la aplicación:

```powershell
python app.py
```

También puedes ejecutarla directamente con:

```powershell
python src\main.py
```

## Datos y seed inicial

- La base de datos se crea automáticamente en `data/minutas.db` al primer inicio.
- Se aplica automáticamente seed del catálogo inicial (arroz, fideos, lentejas, etc.) sin duplicar registros.

## Próximos pasos sugeridos

1. Agregar pruebas unitarias para `services/`.
2. Incorporar repositorios (`repositories/`) si se desea mayor desacople SQL.
3. Definir casos de uso formales (application layer).
4. Añadir migraciones versionadas (Alembic-like o script propio).
