from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from . import constants as const


class CategoriaNoticia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categorías de Noticia"

    def __str__(self):
        return self.nombre


class NivelEducativo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Niveles Educativos"

    def __str__(self):
        return f"{self.nombre}"


class Grado(models.Model):
    numero = models.IntegerField()  # Campo para el número de grado (1-6)
    nivel = models.ForeignKey(
        NivelEducativo, on_delete=models.CASCADE, related_name='grados')

    def clean(self):
        if self.nivel.nombre == 'Primaria' and not (1 <= self.numero <= 6):
            raise ValidationError(
                "El grado de primaria debe estar entre 1 y 6.")
        elif self.nivel.nombre == 'Secundaria' and not (1 <= self.numero <= 5):
            raise ValidationError(
                "El grado de secundaria debe estar entre 1 y 5.")

    def __str__(self):
        return f"{self.numero}° {self.nivel}"


class Seccion(models.Model):
    nombre = models.CharField(max_length=1, unique=True)

    class Meta:
        verbose_name_plural = "Secciones"

    def __str__(self):
        return self.nombre


class Genero(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    nivel = models.ForeignKey(
        NivelEducativo, on_delete=models.CASCADE, related_name='cursos')

    def __str__(self):
        return f"{self.nombre} ({self.nivel.nombre})"


class EstadoAsistencia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    color = models.CharField(
        max_length=7,
        validators=[RegexValidator(
            regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', message="Ingrese un color hexadecimal válido.")]
    )

    class Meta:
        verbose_name_plural = "Estados de Asistencia"

    def __str__(self):
        return self.nombre


class EstadoTarea(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Estados de Tarea"

    def __str__(self):
        return self.nombre


@receiver(post_migrate)
def create_models(sender, **kwargs):
    if sender.name == const.NOMBRE_APLICACION:
        # SECCIONES
        for nombre in const.SECCION_TUPLE:
            Seccion.objects.get_or_create(nombre=nombre)
        # GENEROS
        for nombre in const.GENERO_TUPLE:
            Genero.objects.get_or_create(nombre=nombre)

        # CATEGORIAS
        for nombre in const.CATEGORIAS_NOTICIA_TUPLE:
            CategoriaNoticia.objects.get_or_create(nombre=nombre)
        # NIVELES EDUCATIVOS
        for nombre in const.NIVEL_EDUCATIVO_TUPLE:
            nivel, created = NivelEducativo.objects.get_or_create(
                nombre=nombre)

            # CURSOS
            for nombre in const.CURSO_TUPLE:
                Curso.objects.get_or_create(nombre=nombre, nivel=nivel)

            # GRADOS
            total = 6 if nivel.nombre == "Primaria" else 5
            for grado_numero in range(1, total+1):
                Grado.objects.get_or_create(numero=grado_numero, nivel=nivel)
        # ESTADOS DE ASISTENCIA
        for nombre, color in const.ASISTENCIA_ESTADO_TUPLE:
            EstadoAsistencia.objects.get_or_create(nombre=nombre, color=color)
        # ESTADOS DE TAREA
        for nombre in const.TAREA_ESTADO_TUPLE:
            EstadoTarea.objects.get_or_create(nombre=nombre)
