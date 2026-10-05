# Catálogo de películas

Aplicación de ejemplo para consultar y administrar un catálogo de películas. Se
puede utilizar mediante la documentación web interactiva de FastAPI o desde un
menú numérico en la terminal.

## Estructura de los datos

Las películas se guardan en la variable `movies` en el archivo `main.py`, que es una **lista
de diccionarios** como **modelo de datos normalizado**. Cada elemento de la lista representa una película; las claves
del diccionario son los campos y sus valores contienen los datos. Esta estructura
permite recorrer la lista para buscar, filtrar, agregar, actualizar o eliminar
películas.

Cada película tiene los siguientes campos:

| Campo | Tipo | Formato o restricciones al crear |
| --- | --- | --- |
| `id` | Entero (`int`) | Obligatorio, mayor que 0 y no repetido. |
| `title` | Cadena (`str`) | Obligatoria, entre 3 y 50 caracteres. |
| `overview` | Cadena (`str`) | Obligatoria, entre 10 y 150 caracteres. |
| `release` | Fecha (`date`) | Formato `AAAA-MM-DD`; desde `1970-01-01` hasta la fecha actual. Si se omite, se usa la fecha actual. |
| `rating` | Número decimal (`float`) | Entre 0 y 10. Si se omite, se usa `0.0`. |
| `category` | Cadena (`str`) | Debe ser exactamente uno de los géneros permitidos indicados abajo. |
| `earnings` | Número decimal (`float`) | Mayor o igual que 0. Si se omite, se usa `0.0`. |

Los géneros permitidos para crear películas son: `Comedia`, `Acción`, `Ficción`,
`Romance`, `Aventura`, `Infantil`, `Drama`, `Terror`, `Biográfica` y `Musical`.

FastAPI valida los datos de creación con el modelo `MovieCreate`. El modelo
`Movie` describe los datos completos de una película y `MovieUpdate` describe
los campos que se envían para actualizarla; la actualización no incluye el `id`
en el cuerpo, porque este se indica en la dirección de la solicitud.

> **Almacenamiento:** la lista existe en la memoria del proceso. Los cambios
> realizados desde la API o el menú son visibles mientras el servidor esté
> ejecutándose, pero se pierden al reiniciarlo.

## Preparar y activar el entorno virtual

El proyecto utiliza el entorno virtual llamado `venv`, que contiene Python y las
dependencias de la aplicación.

En Windows PowerShell, desde la carpeta del proyecto, activa el entorno con:

```powershell
.\venv\Scripts\Activate.ps1
```

En Linux o macOS, desde la carpeta del proyecto, el comando equivalente es:

```bash
source venv/bin/activate
```

El archivo `main.py` está dentro de `venv`. Por eso, después de activar el
entorno, sitúate en esa carpeta antes de iniciar Uvicorn:

```powershell
Set-Location  <Unidad_y_ruta_local>\venv
Por ejemplo:
Set-Location D:\pythonapps\fastapi\pabloesdev\venv
```

En Linux o macOS, desde la carpeta del proyecto, utiliza:

```bash
cd venv
```

## Probar la interfaz web de FastAPI

Con el entorno activado y la terminal situada en la carpeta que contiene
`main.py`, inicia el servidor:

```console
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

No cierres esa terminal mientras estés usando la aplicación. En el navegador,
abre <http://127.0.0.1:8000/docs> para probar los endpoints de la API. La ruta
`GET /home` devuelve la lista de películas.

Desde la documentación interactiva también puedes probar estas operaciones:

1. **Listar películas:** [GET /home](http://127.0.0.1:8000/docs#/Movies/get_movie_movies__id__get).
2. **Filtrar película por ID:** [GET /movies/{id}](http://127.0.0.1:8000/docs#/Movies/get_movie_movies__id__get).
3. **Actualizar película:** [PUT /movies/{id}](http://127.0.0.1:8000/docs#/Movies/update_movie_movies__id__put).
4. **Filtrar películas por categoría:** [GET /movies/](http://127.0.0.1:8000/docs#/Movies/get_movies_by_category_movies__get).
5. **Eliminar película:** [DELETE /movies/{id}](http://127.0.0.1:8000/docs#/Movies/delete_movie_movies__id__delete).
6. **Crear una nueva película:** [POST /movies](http://127.0.0.1:8000/docs#/Movies/create_movie_movies_post).

## Probar el menú de terminal

Deja Uvicorn ejecutándose en la primera terminal para que el menú pueda
comunicarse con la API. Abre una **segunda terminal** y ejecuta esta instrucción
única en Windows PowerShell:

```powershell
& 'D:\pythonapps\fastapi\pabloesdev\venv\Scripts\python.exe' 'D:\pythonapps\fastapi\pabloesdev\cli.py'
```

El menú solicita una opción numérica. Después, sigue las preguntas que aparecen
en pantalla. En la opción de modificación, pulsa `Enter` sin escribir un valor
para conservar el dato actual. Elige `0` para salir.

## Operaciones disponibles

| Opción del menú | Operación | Endpoint de FastAPI |
| --- | --- | --- |
| `1` | Listar todas las películas. | `GET /home` |
| `2` | Buscar y mostrar una película por su ID. | `GET /movies/{id}` |
| `3` | Listar películas de un género. | `GET /movies/?category={género}` |
| `4` | Modificar una película identificada por su ID. | `PUT /movies/{id}` |
| `5` | Ingresar una película nueva. | `POST /movies` |
| `0` | Salir del menú. | No realiza una solicitud a la API. |

Para probar una operación, ingresa su número en el menú y pulsa `Enter`.

## Archivo con una lista de películas para probar los endpoints de la API.
Se incluye en el repositorio un documento en formato PDF en el folder docs/ con una lista de películas con datos (datos de películas.pdf), para probar tanto datos correctos, como datos que puede modificar para verificar si la validación y normalización de datos está funcionando correctamente.
Por ejemplo, en lugar de poner la recaudación de forma cruda como 203000000.0, coloca el valor: 203,000,000.0. Notará que se reporta algún tipo de error y se describe con precisión. Igualmento con el resto de tipo de datos y en el ítem género: únicamente se aceptan valores de un listado, descrito en la sección: Estructura de los datos de este archivo [README.md](#estructura-de-los-datos).