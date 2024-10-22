from rest_framework import serializers
from .models import (Apoderado, Estudiante, Docente, Aula, Docente, Tarea,
                     Asistencia, Calificacion, Mensaje, Conversacion, Imagen, Noticia)

from .models_extra import (
    CategoriaNoticia, NivelEducativo, Genero, Curso, EstadoAsistencia, EstadoTarea)


class ApoderadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apoderado
        fields = ['usuario', 'nombres', 'apellidos',
                  'telefono', 'direccion', 'estudiantes']


class ApoderadoRegisterSerializer(serializers.ModelSerializer):  # CAMBIO
    class Meta:
        model = Apoderado
        fields = ['nombres', 'apellidos',
                  'telefono', 'direccion', 'estudiantes']


class DocenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docente
        fields = ['usuario', 'nombres', 'apellidos', 'telefono',
                  'direccion', 'genero', 'fecha_nacimiento', 'curso']


class DocenteRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docente
        fields = ['nombres', 'apellidos', 'telefono',
                  'direccion', 'genero', 'fecha_nacimiento', 'curso']


class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
        fields = ['id', 'nombres', 'apellidos', 'dni']


class AulaSerializer(serializers.ModelSerializer):
    # docentes = serializers.StringRelatedField(many=True)
    grado = serializers.SerializerMethodField()
    seccion = serializers.SerializerMethodField()

    class Meta:
        model = Aula
        fields = ['id', 'nombre', 'grado', 'seccion']

    def get_grado(self, obj):
        return str(obj.grado)

    def get_seccion(self, obj):
        return str(obj.seccion)


class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = "__all__"


class CalificacionSerializer(serializers.ModelSerializer):
    promedio = serializers.ReadOnlyField()

    class Meta:
        model = Calificacion
        fields = ['id', 'calificacion_1','calificacion_2', 'calificacion_3', 'calificacion_4', 'promedio']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convertimos todos los campos a cadenas
        for field in representation:
            if(field != "id"):
                representation[field] = str(representation[field]) if representation[field] is not None else None
        return representation


class ImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen
        fields = ['imagen']


class MensajeSerializer(serializers.ModelSerializer):
    imagenes = ImagenSerializer(many=True, read_only=True)

    class Meta:
        model = Mensaje
        fields = ['id', 'conversacion', 'emisor', 'receptor',
                  'contenido', 'fecha_creacion', 'imagenes']
        read_only_fields = ['fecha_creacion']


class MensajeCrearSerializer(serializers.ModelSerializer):  # COMPLETAR
    class Meta:
        model = Mensaje
        fields = '__all__'


class ConversacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversacion
        fields = '__all__'


class NoticiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Noticia
        fields = ['id','titulo', 'descripcion', 'categoria', 'imagen',
                  'vistas', 'fecha_publicacion', 'administrador']

# EXTRA


class CategoriaNoticiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaNoticia
        fields = "__all__"


class NivelEducativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NivelEducativo
        fields = "__all__"


class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = "__all__"


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = "__all__"


class EstadoAsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoAsistencia
        fields = "__all__"


class EstadoTareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoTarea
        fields = "__all__"
