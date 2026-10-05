from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse
# Para poder usar un esquema de datos para los datos de la película
from pydantic import BaseModel, Field
# Para poder usar el tipo de dato date, se importa la clase date del módulo datetime
from datetime import date
# Para poder definir un tipo de datos opcional en el esquema de datos de la película
from typing import Optional, List

# Para implementar la interfaz web de la API, se importa la clase FastAPI del módulo fastapi
app = FastAPI()

# Modelo de los datos de la película mediante una clase que hereda del BaseModel pydantic
# usado para consultar y registrar películas en la API
class Movie(BaseModel):
    id: int
    title: str
    overview: str
    release: date
    rating: float
    category: str
    earnings: float

# Modelo para crear una nueva película mediante una clase que hereda del BaseModel pydantic
# usado para crear películas en la API
class MovieCreate(BaseModel):
    id: int = Field(gt=0)  # Mayor que 0
    title: str = Field(min_length=3, max_length=50)
    overview: str = Field(min_length=10, max_length=150)
    release: date = Field(
                        default=date.today(),  # Valor por defecto la fecha actual
                        ge=date(1970, 1, 1),    # Mayor o igual que 1 de enero de 1970
                        le=date.today()         # Menor o igual que la fecha actual
                    )
    rating: float = Field(default=0.0, ge=0.0, le=10.0)
    category: str = Field(pattern=r"^(Comedia|Acción|Ficción|Romance|Aventura|Infantil|Drama|Terror|Biográfica|Musical)$")  # Solo se permiten los valores "Comedia", "Acción", "Ficción", "Romance", "Aventura", "Infantil", "Drama", "Terror", "Biográfica" o "Musical"
    earnings: float = Field(default=0.0, ge=0.0)  # Mayor o igual que 0.0

# Modelo de datos de la película mediante una clase que hereda del BaseModel pydantic
# usado para actualizar películas en la API y donde no se utiliza el id de la película
class MovieUpdate(BaseModel):
    title: str
    overview: str
    release: date
    rating: float
    category: str
    earnings: float

# Se crea una lista de diccionarios para almacenar las películas desde el inicio del programa
movies = [
    {
        "id" : 1,
        "title" : "Avatar",
        "overview" : "En Pandora, un exmarine parapléjico en un cuerpo biológico sintético (avatar) debe decidir entre ... pueblo indígena Na'vi.",
        "release" : "2009-12-18",
        "rating" : 8.2,
        "category" : "Acción",
        "earnings" : 2923700000
    },
    {
        "id" : 2,
        "title" : "El hombre de acero",
        "overview" : "Un joven alienígena con poderes sobrehumanos enviado a la Tierra desde Krypton debe asumir el rol de héroe ...",
        "release" : "2013-12-06",
        "rating" : 7.7,
        "category" : "Ficción",
        "earnings" : 663292147
    },
    {
        "id" : 3,
        "title" : "La llegada ",
        "overview" : "Comunicación con extraterrestres que llegan a la tierra ...",
        "release" : "2016-11-11",
        "rating" : 8.5,
        "category" : "Ficción",
        "earnings" : 203388186
    }
]

# app.title = "Mi primera aplicación con FastAPI"
# app.version = "2.0.0"

# Creación de la primera ruta de la API
@app.get("/", tags=["Home"])


@app.get("/home", tags=["Home"])
def get_movies() -> List[Movie]:
    return movies

# Función que se ejecuta cuando se accede a la ruta "/"
# def home():
#    return "Hello world!"

# Devolviendo un diccionario usando el ID
@app.get("/movies/{id}", tags=["Movies"])

# Función que se ejecuta cuando se accede a la ruta "/"
def get_movie(id: int) -> Movie:
    for item in movies:
        if item["id"] == id:
            return item
    return []

# Devolviendo un diccionario de películas usando la categoría
@app.get("/movies/", tags=["Movies"])
def get_movies_by_category(category: str) -> List[Movie]:
    return [item for item in movies if item["category"] == category]


# Método POST para crear una película nueva e ingresarla al diccionario
@app.post("/movies", tags=["Movies"])
def create_movie(movie: MovieCreate) -> List[Movie]:
    # Se agrega la película al diccinario de películas con el método append()
    # y se utiliza el método model_dump() para convertir el objeto movie en un diccionario
    movies.append(movie.model_dump())
    return movies

# Método PUT para actualizar una película
@app.put("/movies/{id}", tags=["Movies"])
def update_movie(id: int, movie: MovieUpdate) -> List[Movie]:
    for item in movies:
        if item["id"] == id:
            item["title"] = movie.title
            item["overview"] = movie.overview
            item["release"] = movie.release
            item["rating"] = movie.rating
            item["category"] = movie.category
            item["earnings"] = movie.earnings

    return movies

# Método DELETE para eliminar una película
@app.delete("/movies/{id}", tags=["Movies"])
def delete_movie(id: int) -> List[Movie]:
    for movie in movies:
        if movie["id"] == id:
            movies.remove(movie)

    return movies
