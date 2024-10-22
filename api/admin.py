from django.contrib import admin
from .models import (Usuario, Administrador, Noticia, Apoderado, Estudiante, Docente, Aula, AulaCurso, Asistencia,
                     Calificacion, Conversacion, Mensaje, Imagen, Estudiante,)

from .models_extra import (CategoriaNoticia, Genero, NivelEducativo,
                           Curso, EstadoAsistencia, EstadoTarea,)


admin.site.register(CategoriaNoticia)
admin.site.register(Genero)
admin.site.register(NivelEducativo)
admin.site.register(Curso)
admin.site.register(EstadoAsistencia)
admin.site.register(EstadoTarea)

admin.site.register(Usuario)
admin.site.register(Administrador)
admin.site.register(Docente)
admin.site.register(Apoderado)
admin.site.register(Estudiante)
admin.site.register(Aula)
admin.site.register(AulaCurso)
admin.site.register(Noticia)
admin.site.register(Asistencia)
admin.site.register(Calificacion)
admin.site.register(Conversacion)
admin.site.register(Mensaje)
admin.site.register(Imagen)
