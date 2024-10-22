from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


from .models_extra import (
    CategoriaNoticia, Curso, Grado, EstadoAsistencia, EstadoTarea, Genero, Seccion)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email debe ser proporcionado")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def create_docente(self, email, password=None, **extra_fields):
        """Crea un usuario con el rol de Docente."""
        extra_fields.setdefault('is_docente', True)
        # Crear el usuario
        user = self.create_user(email, password, **extra_fields)
        return user

    def create_apoderado(self, email, password=None, **extra_fields):
        """Crea un usuario con el rol de Apoderado."""
        extra_fields.setdefault('is_apoderado', True)

        # Crear el usuario
        user = self.create_user(email, password, **extra_fields)

        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Correo electrónico', unique=True)
    # Nuevos campos solicitados
    # Indica si el usuario está en línea
    is_online = models.BooleanField(default=False)
    is_apoderado = models.BooleanField(
        default=False)  # Si el usuario es un apoderado
    is_docente = models.BooleanField(
        default=False)  # Si el usuario es un docente
    # Última vez que actualizó su información
    last_info_updated = models.DateTimeField(null=True, blank=True)
    last_connection = models.DateTimeField(
        null=True, blank=True)  # Última vez que se conectó

    # Para permitir el acceso al admin
    is_staff = models.BooleanField(default=False)
    # Para desactivar cuentas si es necesario
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    groups = models.ManyToManyField(
        Group,
        related_name='usuario_groups',  # Cambia el related_name para evitar el conflicto
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        # Cambia el related_name para evitar el conflicto
        related_name='usuario_permissions',
        blank=True
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def update_last_info(self):
        """Actualiza el campo `last_info_updated` a la fecha actual."""
        self.last_info_updated = timezone.now()
        self.save()

    def update_last_connection(self):
        """Actualiza el campo `last_connection` a la fecha actual."""
        self.last_connection = timezone.now()
        self.save()


class Apoderado(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='apoderado')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=255)
    estudiantes = models.ManyToManyField(
        'Estudiante', related_name='apoderados')

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    @staticmethod
    def obtener_apoderados_por_estudiante(estudiante_id):
        """
        Retorna todos los apoderados asociados a un estudiante dado.
        """
        return Apoderado.objects.filter(estudiantes__id=estudiante_id)


class Docente(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='docente')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=255)
    genero = models.ForeignKey(
        Genero, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_nacimiento = models.DateField()
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name='docentes')

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.curso}"


class Administrador(models.Model):
    user = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='administrador')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Administradores"

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Estudiante(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    dni = models.CharField(max_length=8, unique=True)
    genero = models.ForeignKey(
        Genero, on_delete=models.SET_NULL, null=True, blank=True)
    aula = models.ForeignKey('Aula', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    @staticmethod
    def obtener_estudiantes_por_apoderado(apoderado_id):
        """
        Retorna todos los estudiantes asociados a un apoderado dado.
        """
        return Estudiante.objects.filter(apoderados__id=apoderado_id)


class Aula(models.Model):
    nombre = models.CharField(max_length=100)
    grado = models.ForeignKey(
        Grado, on_delete=models.CASCADE, related_name='aulas', null=True)
    seccion = models.ForeignKey(
        Seccion, on_delete=models.CASCADE, related_name='aulas', null=True)
    docentes = models.ManyToManyField('Docente', through='AulaCurso')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['grado', 'seccion'], name='unique_grado_seccion')
        ]

    def __str__(self):
        return f"{self.nombre} - {self.grado} - '{self.seccion}'"


class AulaCurso(models.Model):
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['aula', 'docente'], name='unique_aula_docente')
        ]

    def clean(self):
        # Verifica que el nivel del curso coincida con el nivel del grado del aula
        if self.docente.curso.nivel != self.aula.grado.nivel:
            raise ValidationError(
                f"El curso {self.docente.curso} no coincide con el nivel educativo del grado '{
                    self.aula.grado.nivel}' del aula."
            )

    @staticmethod
    def obtener_aulas_por_docente(docente_id):
        """
        Retorna todas las aulas donde un docente enseña.
        """
        aulas_ids = AulaCurso.objects.filter(
            docente__id=docente_id).values_list('aula', flat=True).distinct()
        return Aula.objects.filter(id__in=aulas_ids)

    def __str__(self):
        return f"{self.aula} - {self.docente}"


class Tarea(models.Model):
    descripcion = models.TextField()
    fecha_entrega = models.DateField()
    estado = models.ForeignKey(
        EstadoTarea, on_delete=models.CASCADE, null=True, blank=True, related_name='tareas')
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    aulas = models.ManyToManyField(Aula, related_name='tareas')

    def __str__(self):
        return f"{self.descripcion[:50]}..." if len(self.descripcion) > 50 else self.descripcion

def obtener_estado_falta():
    return EstadoAsistencia.objects.filter(nombre="Falto").first()

class Asistencia(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    fecha = models.DateField()
    estado = models.ForeignKey(
        EstadoAsistencia, on_delete=models.CASCADE, null=True, blank=True, related_name='asistencias', default=obtener_estado_falta)

    def __str__(self):
        return f"{self.estudiante} - {self.fecha} - {self.estado}"


class Calificacion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    calificacion_1 = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(20)])
    calificacion_2 = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(20)])
    calificacion_3 = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(20)])
    calificacion_4 = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(20)])
    promedio = models.FloatField(editable=False, default=0.0)

    class Meta:
        verbose_name_plural = "Calificaciones"
        constraints = [
            models.UniqueConstraint(
                fields=['estudiante', 'curso'], name='unique_estudiante_curso')
        ]

    def calcular_promedio(self):
        return (self.calificacion_1 + self.calificacion_2 + self.calificacion_3 + self.calificacion_4) / 4

    def clean(self):
        # Obtener el nivel del curso
        nivel_curso = self.curso.nivel
        
        # Obtener el nivel del aula a través del estudiante
        aula = self.estudiante.aula  # Asumiendo que estudiante tiene un campo aula relacionado
        nivel_aula = aula.grado.nivel  # Asumiendo que aula tiene un campo nivel relacionado con NivelEducativo
        
        # Verificar que ambos niveles coincidan
        if nivel_curso != nivel_aula:
            raise ValidationError("El nivel educativo del curso no coincide con el nivel del aula del estudiante.")
    

    def save(self, *args, **kwargs):
        # Validar antes de guardar
        self.clean() 
        # Calcular el promedio antes de guardar
        self.promedio = self.calcular_promedio()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.estudiante} - Promedio: {self.promedio} ({self.curso.nombre})"


class Conversacion(models.Model):
    participante_1 = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='conversaciones_como_participante_1')
    participante_2 = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='conversaciones_como_participante_2')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Conversaciones"
        unique_together = ('participante_1', 'participante_2')

    def __str__(self):
        return f"Conversación entre {self.participante_1} y {self.participante_2}"

    def clean(self):
        # Verificamos que el participante 1 sea docente y el participante 2 sea apoderado
        if not (self.participante_1.is_docente and self.participante_2.is_apoderado):
            raise ValidationError(
                "El participante 1 debe ser un Docente y el participante 2 debe ser un Apoderado.")

    def save(self, *args, **kwargs):
        # Llamar a clean antes de guardar para asegurarse de que las validaciones se realicen
        self.clean()
        super().save(*args, **kwargs)

    def obtener_mensaje_reciente(self):
        return self.mensajes.order_by('-fecha_creacion').first()

    def obtener_mensajes(self):
        """Obtener todos los mensajes relacionados con esta conversación."""
        return self.mensajes.all()


class Mensaje(models.Model):
    emisor = models.ForeignKey(
        Usuario, related_name='mensajes_enviados', on_delete=models.CASCADE)
    receptor = models.ForeignKey(
        Usuario, related_name='mensajes_recibidos', on_delete=models.CASCADE)
    conversacion = models.ForeignKey(
        Conversacion, related_name='mensajes', on_delete=models.CASCADE, null=True)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Mensaje de {self.emisor} a {self.receptor} en Conversacion con id {self.conversacion.id}'

    def clean(self):
        # Verificamos que el participante 1 sea docente y el participante 2 sea apoderado
        if not (self.emisor.is_docente and self.receptor.is_apoderado):
            raise ValidationError(
                "El participante 1 debe ser un Docente y el participante 2 debe ser un Apoderado.")


def get_upload_to(instance, filename):
    return f'imagenes/mensajes/conversacion_{instance.mensaje.conversacion.id}/{filename}'


class Imagen(models.Model):
    mensaje = models.ForeignKey(
        # Permitir null si es necesario
        Mensaje, related_name='imagenes', on_delete=models.CASCADE, null=True)
    imagen = models.ImageField(upload_to=get_upload_to, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Imagenes"

    def __str__(self):
        return f'Imagen para el mensaje ID: {self.mensaje.id}, ubicado en la conversación ID: {self.mensaje.conversacion.id}'


class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.ForeignKey(
        CategoriaNoticia, on_delete=models.SET_NULL, null=True, blank=True, related_name='categorias')

    imagen = models.ImageField(
        upload_to='imagenes/noticias/', blank=True, null=True)

    vistas = models.IntegerField(default=0)

    fecha_publicacion = models.DateTimeField(default=timezone.now)
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)

    def incrementar_vistas(self, usuario):
        # Incrementar las vistas solo si el usuario no es un administrador
        if not (usuario.is_authenticated and usuario.is_staff):
            self.vistas += 1
            self.save()
            
    def __str__(self):
        categoria = f' - {self.categoria}' if self.categoria else ''
        return f'{self.titulo}{categoria}'

