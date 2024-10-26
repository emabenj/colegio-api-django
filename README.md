# Colegio API
**[Proyecto para aplicativo móvil]**

## Descripción
Este es el backend del proyecto educativo, desarrollado en **Django**. Proporciona una API RESTful y WebSockets para la mensajería en tiempo real.

## Requisitos

- Python 3.x
- Django
- Dependencias adicionales en `requirements.txt`

## Características
- **Roles de Usuario**: Apoderado, Docente y Administrador.
- **Gestión de Noticias**: Noticias categorizadas y con imágenes por defecto.
- **Mensajería en Tiempo Real**: Comunicación entre apoderados y docentes mediante WebSockets.
- **Gestión Académica**: Asignación de cursos y aulas, calificaciones, asistencia y tareas.
- **API REST**: API para manejar datos en el frontend móvil y en web.

## Instalación

### Backend (Django)
1. Clona este repositorio:
    ```bash
    git clone https://github.com/emabenj/colegio-api-django
    ```
2. Crea y activa un entorno virtual:
    ```bash
    python -m venv env
    source env/bin/activate  # En Windows usa `env\Scripts\activate`
    ```
3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4. Realiza las migraciones:
    ```bash
    python manage.py makemigrations
	python manage.py migrate
    python manage.py createsuperuser
    ```
Al ejecutar `python manage.py migrate`, algunos modelos clave de la aplicación se configuran automáticamente gracias a un _receiver_ `post_migrate`. Este proceso crea registros iniciales en la base de datos para algunos modelos como `Seccion`, `Genero`, `CategoriaNoticia`, `NivelEducativo`, `Curso`, `Grado`, `EstadoAsistencia` y `EstadoTarea`, utilizando valores predefinidos que se encuentran en el archivo `constants.py`.

### Modelos y Valores Iniciales
Los valores iniciales se definen en `constants.py`, que contiene tuplas de valores para cada modelo. Al completar el comando `migrate`, Django ejecuta la función `create_models` que usa estos valores para poblar la base de datos. A continuación, se describen los modelos y los valores que se crean:

- **Seccion**: nombres específicos de secciones, definidos en `SECCION_TUPLE`.
- **Genero**: géneros posibles para usuarios, definidos en `GENERO_TUPLE`.
- **CategoriaNoticia**: categorías de noticias, definidas en `CATEGORIAS_NOTICIA_TUPLE`.
- **NivelEducativo**: niveles como Primaria y Secundaria, definidos en `NIVEL_EDUCATIVO_TUPLE`.
- **Curso**: cada nivel tiene sus cursos correspondientes, especificados en `CURSO_TUPLE`.
- **Grado**: grados asociados a cada nivel, con 6 grados para Primaria y 5 para Secundaria.
- **EstadoAsistencia**: distintos estados para la asistencia, definidos en `ASISTENCIA_ESTADO_TUPLE`, cada uno con un color.
- **EstadoTarea**: estados para las tareas, definidos en `TAREA_ESTADO_TUPLE`.
## Uso

1. Ejecuta el servidor de desarrollo de Django:
    ```bash
    daphne -b 0.0.0.0 -p 8000 colegio_bnnm.asgi:application
    ```
3. Puedes acceder al backend en `http://192.168.x.x:8000`.

## Funcionalidades
### Noticias
Las noticias se crean desde el rol de administrador, y pueden ser visualizadas por todos los usuarios. Las categorías de noticias incluyen imágenes predeterminadas cuando no se agrega una específica.

### Gestión de Usuarios y Aulas
- Los administradores pueden registrar apoderados y docentes.
- Los apoderados se registran con un DNI asociado a al menos un estudiante registrado en un aula específica.

### Mensajería en Tiempo Real
Implementada mediante WebSockets para permitir la comunicación entre apoderados y docentes de forma instantánea.
