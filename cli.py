"""Menu interactivo de consola para la API de películas."""

import json
import math
import os
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = os.environ.get("MOVIES_API_URL", "http://127.0.0.1:8000").rstrip("/")
CATEGORIES = (
    "Comedia",
    "Acción",
    "Ficción",
    "Romance",
    "Aventura",
    "Infantil",
    "Drama",
    "Terror",
    "Biográfica",
    "Musical",
)


class APIError(Exception):
    """Error de comunicación o de respuesta de la API."""


def _format_validation_errors(details: Any) -> str:
    """Convierte errores de validación de la API en mensajes en español.

    Args:
        details: Lista de errores recibida en la respuesta de FastAPI.

    Returns:
        Errores traducidos o un mensaje genérico si no hay detalles.
    """
    # Sin una lista de errores, solo se puede mostrar un mensaje genérico.
    if not isinstance(details, list):
        return "La API rechazó los datos enviados."

    messages: list[str] = []
    field_names = {
        "id": "ID",
        "title": "título",
        "overview": "descripción",
        "release": "fecha de estreno",
        "rating": "calificación",
        "category": "género",
        "earnings": "recaudación",
    }

    # Traduce cada error de campo y omite entradas inesperadas.
    for error in details:
        if not isinstance(error, dict):
            continue
        location = error.get("loc", [])
        field = field_names.get(str(location[-1]), "dato") if location else "dato"
        error_type = error.get("type")
        context = error.get("ctx", {})

        # Selecciona una explicación breve según el tipo de validación.
        if error_type == "missing":
            message = "es obligatorio"
        elif error_type in {"int_parsing", "int_type"}:
            message = "debe ser un número entero"
        elif error_type in {"float_parsing", "float_type"}:
            message = "debe ser un número"
        elif error_type in {"date_parsing", "date_from_datetime_parsing"}:
            message = "debe tener el formato AAAA-MM-DD"
        elif error_type == "greater_than":
            message = f"debe ser mayor que {context.get('gt')}"
        elif error_type == "greater_than_equal":
            message = f"debe ser mayor o igual que {context.get('ge')}"
        elif error_type == "less_than_equal":
            message = f"debe ser menor o igual que {context.get('le')}"
        elif error_type == "string_too_short":
            message = f"debe tener al menos {context.get('min_length')} caracteres"
        elif error_type == "string_too_long":
            message = f"no puede superar {context.get('max_length')} caracteres"
        elif error_type == "string_pattern_mismatch":
            message = "no es válido; seleccione un género de la lista indicada"
        else:
            message = "no tiene un formato válido"
        messages.append(f"- El campo {field} {message}.")

    return "\n".join(messages) or "La API rechazó los datos enviados."


def _describe_http_error(error: HTTPError) -> str:
    """Describe en español la respuesta HTTP de error recibida.

    Args:
        error: Excepción HTTP lanzada por la solicitud a la API.

    Returns:
        Mensaje comprensible que resume el error del servidor.
    """
    try:
        body = json.loads(error.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        # Continúa con el código HTTP si el cuerpo no contiene JSON válido.
        body = {}

    # Traduce errores habituales y aprovecha el detalle enviado por la API.
    if error.code == 404:
        return "No se encontró el recurso solicitado."
    if error.code == 422 and isinstance(body, dict):
        return _format_validation_errors(body.get("detail"))
    if isinstance(body, dict) and isinstance(body.get("detail"), str):
        return f"La API respondió con el error HTTP {error.code}: {body['detail']}"
    return f"La API respondió con el error HTTP {error.code}."


def api_request(
    method: str,
    path: str,
    *,
    params: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
) -> Any:
    """Envía una solicitud HTTP a FastAPI y decodifica su respuesta.

    Args:
        method: Verbo HTTP que se enviará, como GET, POST o PUT.
        path: Ruta de la API que se consultará.
        params: Parámetros de consulta opcionales.
        payload: Datos opcionales que se enviarán como JSON.

    Returns:
        Respuesta JSON decodificada o None si no hay contenido.

    Raises:
        APIError: Si falla la conexión o la respuesta no se puede interpretar.
    """
    url = f"{API_URL}{path}"
    # Añade los parámetros solo cuando la operación los requiere.
    if params:
        url = f"{url}?{urlencode(params)}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"} if body is not None else {},
        method=method,
    )

    try:
        with urlopen(request, timeout=5) as response:
            response_body = response.read()
    except HTTPError as error:
        # Convierte los errores HTTP en mensajes adecuados para el menú.
        raise APIError(_describe_http_error(error)) from error
    except (URLError, TimeoutError) as error:
        # Informa de la imposibilidad de contactar con el servidor.
        raise APIError(
            "No se pudo conectar con FastAPI. Compruebe que el servidor esté activo "
            f"en {API_URL}."
        ) from error

    # Las respuestas vacías no contienen JSON que se pueda decodificar.
    if not response_body:
        return None
    try:
        return json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        # Evita exponer la excepción técnica al usuario de la consola.
        raise APIError("La API devolvió una respuesta que no se pudo interpretar.") from error


def read_integer(prompt: str, *, minimum: int | None = None) -> int:
    """Solicita un entero y repite la lectura mientras no sea válido.

    Args:
        prompt: Texto que acompaña la solicitud de entrada.
        minimum: Valor mínimo permitido, si se especifica.

    Returns:
        Entero introducido dentro del rango permitido.
    """
    # Repite la solicitud hasta recibir un entero aceptable.
    while True:
        value = input(prompt).strip()
        try:
            number = int(value)
        except ValueError:
            # El texto no representa un entero; se vuelve a solicitar.
            print("Error: introduzca un número entero.")
            continue
        # Rechaza enteros inferiores al mínimo solicitado.
        if minimum is not None and number < minimum:
            print(f"Error: el valor debe ser mayor o igual que {minimum}.")
            continue
        return number


def read_number(
    prompt: str,
    *,
    default: float | None = None,
    minimum: float | None = None,
    maximum: float | None = None,
    current: float | None = None,
) -> float:
    """Solicita un número finito, respetando valores opcionales y límites.

    Args:
        prompt: Texto que acompaña la solicitud de entrada.
        default: Valor usado si se deja vacío y no hay valor actual.
        minimum: Límite inferior permitido, si se especifica.
        maximum: Límite superior permitido, si se especifica.
        current: Valor que se conserva si la entrada queda vacía.

    Returns:
        Número introducido o valor actual/predeterminado.
    """
    # Repite la solicitud hasta obtener un número válido.
    while True:
        value = input(prompt).strip()
        # En una edición, una entrada vacía conserva el dato existente.
        if not value and current is not None:
            return current
        # Al crear, una entrada vacía puede usar el valor predeterminado.
        if not value and default is not None:
            return default
        try:
            number = float(value)
        except ValueError:
            # Rechaza texto que no se puede convertir en número.
            print("Error: introduzca un número válido.")
            continue
        # Evita aceptar valores infinitos o no numéricos especiales.
        if not math.isfinite(number):
            print("Error: el número debe ser finito.")
            continue
        # Comprueba los límites configurados para el campo.
        if minimum is not None and number < minimum:
            print(f"Error: el valor debe ser mayor o igual que {minimum}.")
            continue
        if maximum is not None and number > maximum:
            print(f"Error: el valor debe ser menor o igual que {maximum}.")
            continue
        return number


def read_date(
    prompt: str,
    *,
    optional: bool = False,
    current: str | None = None,
    validate_bounds: bool = True,
) -> str | None:
    """Solicita una fecha ISO y valida opcionalidad y límites.

    Args:
        prompt: Texto que acompaña la solicitud de entrada.
        optional: Permite dejar vacío el campo si es True.
        current: Fecha que se conserva al dejar vacío durante una edición.
        validate_bounds: Comprueba las fechas mínima y máxima del modelo.

    Returns:
        Fecha en formato AAAA-MM-DD, o None si es opcional y quedó vacía.
    """
    # Repite la lectura hasta recibir una fecha ISO válida.
    while True:
        value = input(prompt).strip()
        # En una edición, vacío significa mantener la fecha existente.
        if not value and current is not None:
            return current
        # En un alta, vacío permite que FastAPI aplique su fecha por defecto.
        if optional and not value:
            return None
        try:
            parsed_date = date.fromisoformat(value)
        except ValueError:
            # La cadena no representa una fecha ISO válida.
            print("Error: introduzca una fecha válida con formato AAAA-MM-DD.")
            continue
        # Comprueba que la fecha esté dentro del intervalo permitido al crear.
        if validate_bounds and parsed_date < date(1970, 1, 1):
            print("Error: la fecha debe ser igual o posterior a 1970-01-01.")
            continue
        if validate_bounds and parsed_date > date.today():
            print("Error: la fecha no puede ser posterior a hoy.")
            continue
        return parsed_date.isoformat()


def read_text(
    prompt: str,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
    current: str | None = None,
) -> str:
    """Solicita texto y verifica su presencia y longitud.

    Args:
        prompt: Texto que acompaña la solicitud de entrada.
        minimum: Longitud mínima permitida, si se especifica.
        maximum: Longitud máxima permitida, si se especifica.
        current: Texto que se conserva al dejar vacío durante una edición.

    Returns:
        Texto introducido o el texto actual.
    """
    # Repite la solicitud hasta cumplir las restricciones del campo.
    while True:
        value = input(prompt).strip()
        # En una edición, vacío conserva el valor actual.
        if not value and current is not None:
            return current
        # Rechaza texto fuera de los límites de longitud indicados.
        if minimum is not None and len(value) < minimum:
            print(f"Error: el texto debe tener al menos {minimum} caracteres.")
            continue
        if maximum is not None and len(value) > maximum:
            print(f"Error: el texto no puede superar {maximum} caracteres.")
            continue
        # Los campos obligatorios no pueden quedar vacíos.
        if not value:
            print("Error: este campo es obligatorio.")
            continue
        return value


def read_category(*, current: str | None = None) -> str:
    """Solicita un género permitido o conserva el actual en una edición.

    Args:
        current: Género que se conserva si la entrada queda vacía.

    Returns:
        Género incluido en la lista de categorías permitidas.
    """
    choices = ", ".join(CATEGORIES)
    # Repite hasta recibir una categoría permitida.
    while True:
        value = input(f"Género ({choices})").strip()
        # En una edición, vacío conserva la categoría existente.
        if not value and current is not None:
            return current
        # Solo acepta coincidencias exactas con las categorías configuradas.
        if value in CATEGORIES:
            return value
        print(f"Error: seleccione exactamente uno de estos géneros: {choices}.")


def print_movies(movies: Any) -> None:
    """Muestra una lista de películas con sus campos principales.

    Args:
        movies: Valor recibido de la API, esperado como lista de diccionarios.

    Returns:
        None; imprime los resultados o un mensaje explicativo.
    """
    # Comprueba primero el tipo para evitar recorrer una respuesta inesperada.
    if not isinstance(movies, list):
        print("Error: la API no devolvió una lista de películas.")
        return
    # Informa si la lista no contiene películas.
    if not movies:
        print("No se encontraron películas.")
        return

    # Imprime todos los campos de cada película recibida.
    for movie in movies:
        print(
            f"\nID: {movie['id']}\n"
            f"Título: {movie['title']}\n"
            f"Descripción: {movie['overview']}\n"
            f"Estreno: {movie['release']}\n"
            f"Calificación: {movie['rating']}\n"
            f"Género: {movie['category']}\n"
            f"Recaudación: {movie['earnings']}"
        )


def list_movies() -> None:
    """Solicita y muestra todas las películas.

    Returns:
        None; imprime la lista recibida de la API.
    """
    print_movies(api_request("GET", "/home"))


def select_movie_by_id() -> None:
    """Busca una película por ID y la muestra si existe.

    Returns:
        None; imprime el resultado o un aviso si no existe.
    """
    movie_id = read_integer("ID de la película: ", minimum=1)
    movies = api_request("GET", "/home")
    movie = next(
        (item for item in movies if item["id"] == movie_id),
        None,
    )
    # Informa si el ID no está presente en el catálogo.
    if movie is None:
        print(f"No existe una película con ID {movie_id}.")
        return
    print_movies([api_request("GET", f"/movies/{movie_id}")])


def select_movies_by_category() -> None:
    """Solicita un género y muestra sus películas coincidentes.

    Returns:
        None; imprime las películas encontradas.
    """
    category = read_category()
    print_movies(api_request("GET", "/movies/", params={"category": category}))


def update_movie() -> None:
    """Solicita los cambios de una película existente y los envía a la API.

    Returns:
        None; informa cuando la actualización termina correctamente.
    """
    movie_id = read_integer("ID de la película que desea modificar: ", minimum=1)
    movies = api_request("GET", "/home")
    current = next((item for item in movies if item["id"] == movie_id), None)
    # Evita solicitar cambios si no existe una película con ese ID.
    if current is None:
        print(f"No existe una película con ID {movie_id}.")
        return

    print("Deje el campo vacío para conservar su valor actual.")
    payload = {
        "title": read_text(
            f"Título [{current['title']}]: ",
            minimum=3,
            maximum=50,
            current=current["title"],
        ),
        "overview": read_text(
            f"Descripción [{current['overview']}]: ",
            minimum=10,
            maximum=150,
            current=current["overview"],
        ),
        "release": read_date(
            f"Fecha de estreno AAAA-MM-DD [{current['release']}]: ",
            current=current["release"],
            validate_bounds=False,
        ),
        "rating": read_number(
            f"Calificación 0-10 [{current['rating']}]: ",
            current=current["rating"],
        ),
        "category": read_category(current=current["category"]),
        "earnings": read_number(
            f"Recaudación [{current['earnings']}]: ",
            current=current["earnings"],
        ),
    }
    api_request("PUT", f"/movies/{movie_id}", payload=payload)
    print("Película modificada correctamente.")


def create_movie() -> None:
    """Solicita los datos de una película nueva y la crea mediante la API.

    Returns:
        None; informa cuando la película se crea correctamente.
    """
    print(
        "\nDatos esperados para una nueva película:\n"
        "- ID: entero mayor que 0 (obligatorio y no repetido).\n"
        "- Título: texto de 3 a 50 caracteres (obligatorio).\n"
        "- Descripción: texto de 10 a 150 caracteres (obligatoria).\n"
        "- Fecha de estreno: AAAA-MM-DD, entre 1970-01-01 y hoy "
        "(opcional; vacío usa la fecha actual).\n"
        "- Calificación: número entre 0 y 10 (opcional; vacío usa 0).\n"
        f"- Género: uno de {', '.join(CATEGORIES)} (obligatorio).\n"
        "- Recaudación: número mayor o igual que 0 (opcional; vacío usa 0).\n"
    )

    existing_movies = api_request("GET", "/home")
    movie_id = read_integer("ID: ", minimum=1)
    # Impide reutilizar un ID que ya pertenece a otra película.
    while any(movie["id"] == movie_id for movie in existing_movies):
        print(f"Error: ya existe una película con ID {movie_id}.")
        movie_id = read_integer("Introduzca otro ID: ", minimum=1)

    payload: dict[str, Any] = {
        "id": movie_id,
        "title": read_text("Título: ", minimum=3, maximum=50),
        "overview": read_text("Descripción: ", minimum=10, maximum=150),
    }

    release = read_date("Fecha de estreno [vacío = hoy]: ", optional=True)
    # Solo envía la fecha si se indicó; de otro modo aplica el valor del modelo.
    if release is not None:
        payload["release"] = release

    payload["rating"] = read_number(
        "Calificación [vacío = 0]: ",
        default=0,
        minimum=0,
        maximum=10,
    )
    payload["category"] = read_category()
    payload["earnings"] = read_number(
        "Recaudación [vacío = 0]: ",
        default=0,
        minimum=0,
    )

    api_request("POST", "/movies", payload=payload)
    print("Película ingresada correctamente.")


def show_menu() -> None:
    """Presenta el menú y ejecuta opciones hasta que el usuario salga.

    Returns:
        None; termina al seleccionar la opción de salida.
    """
    # Mantiene el menú activo después de cada operación.
    while True:
        print(
            "\n=== Menú de películas ===\n"
            "1) Listar las películas\n"
            "2) Seleccionar película por ID\n"
            "3) Seleccionar películas por género\n"
            "4) Modificar película\n"
            "5) Ingresar nueva película\n"
            "0) Salir"
        )
        option = input("Seleccione una opción: ").strip()

        # La opción cero termina el ciclo del menú.
        if option == "0":
            print("Hasta luego.")
            return
        actions = {
            "1": list_movies,
            "2": select_movie_by_id,
            "3": select_movies_by_category,
            "4": update_movie,
            "5": create_movie,
        }
        action = actions.get(option)
        # Rechaza opciones que no correspondan a ninguna operación.
        if action is None:
            print("Error: seleccione una opción válida del menú.")
            continue
        try:
            action()
        except APIError as error:
            # Muestra en español errores de conexión o respuestas de la API.
            print(f"Error: {error}")
        except (KeyError, TypeError):
            # Avisa si la respuesta no tiene la estructura que espera el menú.
            print("Error: la respuesta de FastAPI tiene un formato inesperado.")


if __name__ == "__main__":
    # Muestra el menú solo al ejecutar este archivo directamente.
    show_menu()
