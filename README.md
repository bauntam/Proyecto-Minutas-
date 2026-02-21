# MVP Minutas por Jardín (Tkinter + SQLite)

Aplicación de escritorio simple para crear y gestionar **jardines**, **minutas**, **ingredientes en gramos** y el **pedido semanal** por jardín.
Está pensada para una primera entrega usable y estable.

## Funcionalidades incluidas

- **Catálogo de alimentos**
  - Carga inicial automática al primer arranque.
  - Alta de nuevos alimentos desde interfaz.
  - Evita duplicados por nombre (sin importar mayúsculas/minúsculas ni espacios extra).
- **Jardines**
  - Crear, listar, renombrar y eliminar.
- **Plan semanal por jardín**
  - Asignar minutas a una semana por jardín.
  - Agregar ingredientes desde catálogo con gramos por 2 grupos etarios.
  - Editar gramos y quitar ingredientes.
  - Listar y abrir minutas para edición.

- **Pedido semanal (MVP)**
  - Selección de jardín y múltiples minutas de la semana.
  - Ingreso de # de niños por grupo etario.
  - Consolidación por alimento sumando minutas repetidas y cálculo de totales.

- **Minutas (importación por Excel)**
  - Descargar plantilla `.xlsx` con alimentos en orden alfabético.
  - Importar minutas masivamente desde Excel (nombre de minuta + gramos para 2 grupos etarios).
  - Compara el nombre del alimento contra el catálogo y carga los gramos automáticamente.
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
  excel_minutas.py # Plantilla e importación de minutas por Excel
  seed.py          # Catálogo inicial
requirements.txt
README.md
```

## Base de datos

Tablas:

- `alimentos(id, nombre UNIQUE)`
- `jardines(id, nombre UNIQUE)`
- `minutas(id, nombre, fecha_creacion)`
- `minuta_items(id, minuta_id, alimento_id, gramos_1_2, gramos_3_5)`
- `jardin_minutas_semana(id, jardin_id, minuta_id, orden)`

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


## Importar minutas desde Excel

En **Gestión de minutas** ahora hay dos botones:

- **Descargar plantilla Excel**: genera un archivo con columnas:
  - `minuta`
  - `alimento`
  - `gramos_grupo_1`
  - `gramos_grupo_2`
- **Importar Excel**: lee el archivo y crea/actualiza minutas y gramos para ambos grupos etarios.

Reglas:

- Los nombres de alimentos deben coincidir con el catálogo (comparación por texto normalizado).
- Cada fila representa un alimento dentro de una minuta.
- Si la minuta no existe, se crea automáticamente.
- Si la minuta ya existe, se actualizan sus alimentos.
- Los gramos de ambos grupos deben ser números mayores a 0.


## Cómo generar pedido semanal

1. En la pantalla principal, haz clic en **Pedido semanal**.
2. Selecciona el **jardín**.
3. En la lista de minutas, selecciona varias usando `Ctrl`/`Shift` (selección múltiple).
4. Ingresa **#Niños Grupo 1** y **#Niños Grupo 2** (enteros `>= 0`).
5. Haz clic en **Calcular**.
6. Se mostrará una tabla resumen con columnas:
   - `Alimento`
   - `Suma gramos G1`, `#Niños G1`, `Total G1`
   - `Suma gramos G2`, `#Niños G2`, `Total G2`
   - `Total general`

Reglas de cálculo:

- El pedido usa la **UNIÓN total de alimentos** de todas las minutas seleccionadas.
  - Si un alimento aparece en al menos 1 minuta, debe aparecer en el consolidado final.
  - Si no aparece en alguna minuta seleccionada, para esa minuta su aporte se toma como `0` (no se elimina del pedido).
- `suma_gramos_g1 = Σ(gramos_1_2 del alimento en minutas seleccionadas; si no existe fila en una minuta, suma 0)`
- `suma_gramos_g2 = Σ(gramos_3_5 del alimento en minutas seleccionadas; si no existe fila en una minuta, suma 0)`
- `total_g1 = suma_gramos_g1 * #niños_grupo_1`
- `total_g2 = suma_gramos_g2 * #niños_grupo_2`
- `total_general = total_g1 + total_g2`

La tabla se ordena alfabéticamente por alimento.
