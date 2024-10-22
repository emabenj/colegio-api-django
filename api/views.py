from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
# from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, generics, status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import ReadOnlyForAll, ReadOnlyForDocente, ReadOnlyForApoderado, DocenteAdminPermission, DocenteApoderadoPermission, ControlApoderadoPermission, ControlDocentePermission
from .serializer import (ApoderadoSerializer, ApoderadoRegisterSerializer, DocenteSerializer, DocenteRegisterSerializer, EstudianteSerializer, AulaSerializer, TareaSerializer, CalificacionSerializer, MensajeSerializer, MensajeCrearSerializer, ConversacionSerializer, ImagenSerializer, NoticiaSerializer,
                         CategoriaNoticiaSerializer, NivelEducativoSerializer, GeneroSerializer, CursoSerializer, EstadoAsistenciaSerializer, EstadoTareaSerializer)
from .models import (Noticia, Apoderado, Estudiante, Docente, Administrador, Mensaje,
                     Aula, Tarea, AulaCurso, Asistencia, Calificacion, Usuario, Conversacion, Imagen)
from .models_extra import (NivelEducativo, Curso,
                           EstadoAsistencia, EstadoTarea, CategoriaNoticia, Genero)
from .helper_functions import BHelperFunctions as helper
from .constants import TOTAL_APODERADOS_POR_ESTUDIANTE as total_apoderados


class CategoriaView(viewsets.ModelViewSet):
    permission_classes = (ReadOnlyForAll,)
    serializer_class = CategoriaNoticiaSerializer
    queryset = CategoriaNoticia.objects.all()


class GeneroView(viewsets.ModelViewSet):
    permission_classes = (ReadOnlyForAll,)
    serializer_class = GeneroSerializer
    queryset = Genero.objects.all()


class NivelView(viewsets.ModelViewSet):
    permission_classes = (ReadOnlyForAll,)
    serializer_class = NivelEducativoSerializer
    queryset = NivelEducativo.objects.all()


class CursoView(viewsets.ModelViewSet):
    permission_classes = (ReadOnlyForAll,)
    serializer_class = CursoSerializer
    queryset = Curso.objects.all()


class EstadoAsistenciaView(viewsets.ModelViewSet):
    permission_classes = (ReadOnlyForAll,)
    serializer_class = EstadoAsistenciaSerializer
    queryset = EstadoAsistencia.objects.all()


class EstadoTareaView(viewsets.ModelViewSet):
    permission_classes = (ReadOnlyForAll,)
    serializer_class = EstadoTareaSerializer
    queryset = EstadoTarea.objects.all()


class NoticiaView(viewsets.ModelViewSet):
    permission_classes = (ReadOnlyForAll,)
    serializer_class = NoticiaSerializer
    queryset = Noticia.objects.all()

    def retrieve(self, request, *args, **kwargs):
        # Obtener la instancia de la noticia
        noticia = self.get_object()
        # Incrementar las vistas solo si el usuario tiene uno de los roles permitidos
        usuario = request.user
        # if usuario.is_authenticated and (usuario.is_apoderado or usuario.is_docente):
        noticia.incrementar_vistas(usuario)

        # Serializar y devolver la noticia
        serializer = self.get_serializer(noticia)
        return Response(serializer.data)


class ApoderadoView(viewsets.ModelViewSet):
    permission_classes = (ControlApoderadoPermission,)
    serializer_class = ApoderadoSerializer
    queryset = Apoderado.objects.all()

    def update(self, request, *args, **kwargs):
        apoderado = self.get_object()

        # Verificar si el usuario autenticado es el mismo que el apoderado o es un admin
        if request.user != apoderado.usuario and not request.user.is_staff:
            raise PermissionDenied(
                "No tienes permiso para actualizar esta información.")

        # Actualizar el correo del usuario asociado si está en la solicitud
        email = request.data.get('email', None)
        if email and apoderado.usuario.email != email:
            if Usuario.objects.filter(email=email).exists():
                raise ValidationError(
                    {"email": "Este correo electrónico ya está en uso."})
            apoderado.usuario.email = email
        apoderado.usuario.last_profile_update = timezone.now()
        apoderado.usuario.save()

        # Si la verificación pasa, permitir la actualización
        super().update(request, *args, **kwargs)
        return Response({"message": "Información actualizada correctamente."}, status=status.HTTP_200_OK)


class EstudianteView(viewsets.ModelViewSet):
    permission_classes = (ReadOnlyForDocente, ReadOnlyForApoderado,)
    serializer_class = EstudianteSerializer
    queryset = Estudiante.objects.all()

    def list(self, request):
        dni = request.query_params.get('dni')

        if not dni:
            return Response({"details": "No se ingresó un dni para buscar a un estudiante."}, status=400)

        try:
            estudiante = Estudiante.objects.get(
                dni=dni)
        except Estudiante.DoesNotExist:
            raise NotFound("Estudiante no encontrado.")

        # Contar el número de apoderados asociados al estudiante
        numero_apoderados = estudiante.apoderados.count()

        # Verificar si el número de apoderados es mayor o igual a 5
        if numero_apoderados >= total_apoderados:
            return Response({"details": "El estudiante ya tiene el número máximo permitido de apoderados (5)."}, status=400)

        serializer = EstudianteSerializer(estudiante)
        return Response(serializer.data)


class DocenteView(viewsets.ModelViewSet):
    permission_classes = (ControlDocentePermission,)
    serializer_class = DocenteSerializer
    queryset = Docente.objects.all()

    def update(self, request, *args, **kwargs):
        docente = self.get_object()

        # Verificar si el usuario autenticado es el mismo que el apoderado o es un admin
        if request.user != docente.usuario and not request.user.is_staff:
            raise PermissionDenied(
                "No tienes permiso para actualizar esta información.")

        # Actualizar el correo del usuario asociado si está en la solicitud
        email = request.data.get('email', None)
        if email and docente.usuario.email != email:
            if Usuario.objects.filter(email=email).exists():
                raise ValidationError(
                    {"email": "Este correo electrónico ya está en uso."})
            docente.usuario.email = email
        docente.usuario.last_profile_update = timezone.now()
        docente.usuario.save()  # Guardar los cambios en el usuario

        # Si la verificación pasa, permitir la actualización del resto de la información del docente
        super().update(request, *args, **kwargs)
        return Response({"message": "Información actualizada correctamente."}, status=status.HTTP_200_OK)


class AulaView(viewsets.ModelViewSet):
    permission_classes = (ReadOnlyForDocente,)
    serializer_class = AulaSerializer
    queryset = Aula.objects.all()


class TareaView(viewsets.ModelViewSet):
    permission_classes = (DocenteAdminPermission,)
    serializer_class = TareaSerializer
    queryset = Tarea.objects.all()

    def list(self, request):
        docente_id = request.query_params.get('docente')
        aula_id = request.query_params.get('aula')

        if docente_id and aula_id:
            try:
                # Obtener las aulas del docente
                aulas_docente = AulaCurso.objects.filter(
                    docente_id=docente_id).values_list('aula_id', flat=True)

                # Verificar si el aula_id está en las aulas del docente
                if int(aula_id) in aulas_docente:
                    # Obtener las tareas asociadas al aula
                    tareas = Tarea.objects.filter(
                        aulas__id=aula_id, docente_id=docente_id)
                else:
                    return Response({"details": "El aula no está asociada al docente."}, status=400)
            except ValueError:
                return Response({"details": "ID inválido."}, status=400)
        else:
            return Response({"details": "docente_id y aula_id son necesarios."}, status=400)

        serializer = TareaSerializer(tareas, many=True)
        return Response(serializer.data)


class AsistenciaViewSet(viewsets.ViewSet):
    permission_classes = (DocenteAdminPermission,)

    # @action(detail=False, methods=['get', 'patch'], url_path='aula/(?P<aula_id>\d+)')
    @action(detail=False, methods=['get', 'patch'], url_path=r'aula/(?P<aula_id>\d+)')
    def aula(self, request, aula_id=None):
        # Obtener la fecha actual
        fecha_actual = timezone.now().date()

        # Obtener los estudiantes del aula
        estudiantes = Estudiante.objects.filter(aula_id=aula_id)

        # Obtener el estado 'Falta' de la asistencia
        # estado_falta, _ = EstadoAsistencia.objects.get_or_create(nombre='Falta')

        if request.method == 'GET':
            # Crear las asistencias si no existen
            asistencias = []
            for estudiante in estudiantes:
                asistencia, created = Asistencia.objects.get_or_create(
                    estudiante=estudiante,
                    fecha=fecha_actual
                )
                asistencias.append({
                    'id': asistencia.id,
                    'estudiante_id': estudiante.id,
                    'fecha': asistencia.fecha,
                    'nombres': estudiante.nombres,
                    'apellidos': estudiante.apellidos,
                    'genero': estudiante.genero.id,
                    'estado': asistencia.estado.id,
                })
            return Response(asistencias, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            # Actualizar las asistencias
            data = request.data  # Lista de asistencias a actualizar
            for asistencia_data in data:
                try:
                    asistencia = Asistencia.objects.get(
                        id=asistencia_data['id'])
                    # Obtener el nuevo estado desde los datos proporcionados
                    estado_id = asistencia_data.get('estado', None)
                    if estado_id:
                        try:
                            # Buscar el estado por nombre en la base de datos
                            nuevo_estado = EstadoAsistencia.objects.get(
                                id=estado_id)
                            asistencia.estado = nuevo_estado  # Asignar el nuevo estado
                        except EstadoAsistencia.DoesNotExist:
                            return Response(
                                {"details": f"No existe el estado con id '{
                                    estado_id}'."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    asistencia.save()
                except Asistencia.DoesNotExist:
                    return Response({"details": "Asistencia no encontrada."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Asistencias actualizadas correctamente."}, status=status.HTTP_200_OK)


class CalificacionView(viewsets.ModelViewSet):
    permission_classes = (DocenteAdminPermission,)
    serializer_class = CalificacionSerializer
    queryset = Calificacion.objects.all()

    def list(self, request):
        curso_id = request.query_params.get('curso')
        estudiante_id = request.query_params.get('estudiante')

        if not curso_id or not estudiante_id:
            return Response({"details": "El id del curso y del estudiante son necesarios."}, status=400)

        try:
            # Intentar obtener la calificación existente
            calificacion = Calificacion.objects.get(
                curso_id=curso_id, estudiante_id=estudiante_id)
        except Calificacion.DoesNotExist:
            # Si no existe la calificación, crear una nueva
            estudiante = Estudiante.objects.get(id=estudiante_id)
            curso = Curso.objects.get(id=curso_id)

            calificacion = Calificacion.objects.create(
                curso=curso,
                estudiante=estudiante,
            )

        # Serializar y devolver la calificación existente o la recién creada
        serializer = CalificacionSerializer(calificacion)
        return Response(serializer.data)


class ConversacionView(viewsets.ModelViewSet):
    permission_classes = (DocenteApoderadoPermission,)
    serializer_class = ConversacionSerializer
    queryset = Conversacion.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """Obtiene o crea una conversación entre los participantes."""
        receptor_id = request.query_params.get('participante_2')

        if not receptor_id:
            return Response({"details": "Participante receptor necesario."}, status=400)

        # Obtener el usuario autenticado
        usuario = request.user
        if not usuario:
            return Response({"details": "Usuario no authenticado."}, status=400)

        try:
            receptor_usuario = Usuario.objects.get(id=receptor_id)
            participante_1 = usuario if usuario.is_docente else receptor_usuario
            participante_2 = usuario if usuario.is_apoderado else receptor_usuario
        except Usuario.DoesNotExist:
            return Response({"details": "Participante no encontrado."}, status=404)

        # Verificar si ya existe una conversación entre los participantes
        conversacion = Conversacion.objects.filter(
            (Q(participante_1=participante_1, participante_2=participante_2) |
             Q(participante_1=participante_2, participante_2=participante_1))
        ).first()

        if conversacion:
            serializer = self.get_serializer(conversacion)
            return Response(serializer.data)

        # Si no existe la conversación, crearla
        if not (participante_1.is_docente and participante_2.is_apoderado):
            return Response({"details": "El primer participante debe ser Docente y el segundo Apoderado."}, status=400)

        conversacion = Conversacion.objects.create(
            participante_1=participante_1,
            participante_2=participante_2
        )
        serializer = self.get_serializer(conversacion)
        return Response(serializer.data, status=201)

    def list(self, request, *args, **kwargs):
        # Obtener el usuario autenticado
        usuario = request.user

        # Filtrar las conversaciones donde el usuario sea participante
        conversaciones = Conversacion.objects.filter(
            Q(participante_1=usuario) | Q(participante_2=usuario)
        )

        resultado = []
        for conversacion in conversaciones:
            # Obtener el mensaje más reciente
            mensaje_reciente = conversacion.obtener_mensaje_reciente()
            if mensaje_reciente:
                mensaje_serializado = MensajeSerializer(mensaje_reciente).data
            else:
                mensaje_serializado = "No hay mensajes"

            # Agregar al resultado la conversación y su mensaje más reciente
            resultado.append({
                'conversacion': ConversacionSerializer(conversacion).data,
                'mensaje_reciente': mensaje_serializado
            })
        return Response(resultado)

    @action(detail=True, methods=['get'])
    def mensajes(self, request, pk=None):
        """Obtener los mensajes de una conversación, si el usuario pertenece a ella"""
        # Obtener la conversación
        conversacion = get_object_or_404(Conversacion, pk=pk)

        # Obtener el usuario autenticado
        usuario = request.user

        # Comprobar si el usuario es parte de la conversación
        if usuario != conversacion.participante_1 and usuario != conversacion.participante_2:
            return Response({"details": "No tienes permiso para ver los mensajes de esta conversación."}, status=status.HTTP_403_FORBIDDEN)

        # Obtener los mensajes de la conversación
        mensajes = conversacion.obtener_mensajes()

        # Serializar los mensajes
        mensajes_serializer = MensajeSerializer(mensajes, many=True)

        return Response(mensajes_serializer.data, status=status.HTTP_200_OK)


class MensajeView(viewsets.ModelViewSet):
    permission_classes = (DocenteApoderadoPermission,)
    serializer_class = MensajeCrearSerializer
    queryset = Mensaje.objects.all()

    def create(self, request, *args, **kwargs):
        emisor_id = request.data.get('emisor')
        receptores_ids = [int(i)
                          for i in request.data.get('receptores').split(".")]
        contenido = request.data.get('contenido')

        if not emisor_id or not receptores_ids or not contenido:
            return Response({"details": "Emisor, receptores y contenido necesarios."}, status=400)

        try:
            emisor = Usuario.objects.get(id=emisor_id)
        except Usuario.DoesNotExist:
            return Response({"details": "Usuario no encontrado."}, status=404)

        mensajes_enviados = []

        for receptor_id in receptores_ids:
            try:
                receptor = Usuario.objects.get(id=receptor_id)
            except Usuario.DoesNotExist:
                return Response({"details": f"Receptor {receptor_id} no encontrado."}, status=404)

            if not ((emisor.is_apoderado and receptor.is_docente) or
                    (emisor.is_docente and receptor.is_apoderado)):
                return Response({"details": "El mensaje debe ser entre un apoderado y un docente."}, status=400)

            # Verificar si existe una conversación, crearla si no
            conversacion, creada = Conversacion.objects.get_or_create(
                participante_1=emisor if emisor.is_docente else receptor,
                participante_2=receptor if receptor.is_apoderado else emisor,
                # defaults={'ultima_actualizacion': timezone.now()}
            )

            # Crea el mensaje
            mensaje = Mensaje.objects.create(
                emisor=emisor,
                receptor=receptor,
                conversacion=conversacion,
                contenido=request.data.get('contenido')
            )

            # Verifica si hay una imagen en la solicitud
            if 'imagen' in request.FILES:
                imagen_file = request.FILES['imagen']
                # Crea una instancia de Imagen asociada al mensaje
                Imagen.objects.create(mensaje=mensaje, imagen=imagen_file)

            # Recarga el mensaje desde la base de datos para incluir las imágenes recién asociadas
            mensaje.refresh_from_db()

            # Agregar el mensaje a la lista de mensajes enviados
            mensajes_enviados.append(mensaje)

        # Serializar todos los mensajes enviados y devolverlos
        serializer = MensajeSerializer(mensajes_enviados, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ImagenView(viewsets.ModelViewSet):
    permission_classes = (DocenteApoderadoPermission,)
    serializer_class = ImagenSerializer
    queryset = Imagen.objects.all()


class AulasPorDocenteView(viewsets.ViewSet):
    permission_classes = (ReadOnlyForDocente,)

    def retrieve(self, request, pk=None):
        docente_id = pk
        aulas = AulaCurso.obtener_aulas_por_docente(docente_id=docente_id)
        if not aulas:
            return Response({'details': 'Docente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        resultado = []

        for aula in aulas:
            # Obtener los estudiantes del aula
            estudiantes = Estudiante.objects.filter(aula=aula)
            estudiantes_data = []

            apoderados_id = set()

            for estudiante in estudiantes:
                # Obtener los apoderados del estudiante
                apoderados = Apoderado.obtener_apoderados_por_estudiante(
                    estudiante.id)
                apoderados_data = []

                for apoderado in apoderados:
                    if apoderado.usuario.id not in apoderados_id:
                        apoderados_id.add(apoderado.usuario.id)
                    apoderado_data = {
                        'usuario_id': apoderado.usuario.id,
                        'nombres': apoderado.nombres,
                        'apellidos': apoderado.apellidos,
                        'email': apoderado.usuario.email,
                    }
                    apoderados_data.append(apoderado_data)

                # Añadir la información del estudiante junto con sus apoderados
                estudiantes_data.append({
                    'id': estudiante.id,
                    'nombres': estudiante.nombres,
                    'apellidos': estudiante.apellidos,
                    'genero': estudiante.genero.id,
                    'apoderados': apoderados_data,
                })
            # Contar el número de apoderados por estudiante
            total_apoderados = len(apoderados_id)

            # Agregar la información del aula con estudiantes y la cantidad de apoderados
            resultado.append({
                'id': aula.id,
                'nombre': aula.nombre,
                'grado': str(aula.grado),
                'seccion': aula.seccion.nombre,
                'estudiantes': estudiantes_data,
                'apoderados': total_apoderados,
            })

        return Response(resultado)  # Response({'resultado': resultado})


class EstudiantesPorApoderadoView(viewsets.ViewSet):
    permission_classes = (ReadOnlyForApoderado,)

    def retrieve(self, request, pk=None):
        apoderado_id = pk
        estudiantes = Estudiante.obtener_estudiantes_por_apoderado(
            apoderado_id=apoderado_id)
        if not estudiantes:
            return Response({'details': 'Apoderado no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        resultado = []
        for estudiante in estudiantes:
            # Obtener la información del aula
            aula = estudiante.aula
            # Serializar la información del aula
            aula_info = AulaSerializer(aula).data

            # Obtener los docentes asociados al aula del estudiante
            aula_cursos = AulaCurso.objects.filter(aula=estudiante.aula)
            docentes_info = []
            for aula_curso in aula_cursos:
                docente = aula_curso.docente
                docentes_info.append({
                    'usuario_id': docente.usuario.id,
                    'nombres': docente.nombres,
                    'apellidos': docente.apellidos,
                    'email': docente.usuario.email,
                    'curso': docente.curso.id if docente.curso else None,
                })

            # Construir la respuesta para cada estudiante
            estudiante_info = {
                'id': estudiante.id,
                'nombres': estudiante.nombres,
                'apellidos': estudiante.apellidos,
                'genero': estudiante.genero.id,
                'aula': aula_info,
                'docentes': docentes_info,  # Lista de docentes
            }

            resultado.append(estudiante_info)

        return Response(resultado, status=status.HTTP_200_OK)


class RegisterDocenteView(generics.CreateAPIView):
    permission_classes = (IsAdminUser,)
    queryset = Docente.objects.all()
    serializer_class = DocenteRegisterSerializer

    def perform_create(self, serializer):
        email = self.request.data.get('email')
        telefono = self.request.data.get('telefono')

        # Verificar si el teléfono ya está registrado
        if Docente.objects.filter(telefono=telefono).exists():
            raise serializers.ValidationError(
                {"details": "El número de teléfono ya está registrado."})

        # Verificar si el correo ya está registrado
        if Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"details": "El correo electrónico ya está registrado."})

        # Generar una contraseña aleatoria
        password = helper.generate_password()
        print(password)
        user = Usuario.objects.create_docente(
            email=email, password=password)
        serializer.save(usuario=user)
        # Preparar la respuesta con el mensaje personalizado
        response_data = serializer.data
        response_data["message"] = "Contraseña enviada al correo"
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class RegisterApoderadoView(generics.CreateAPIView):
    permission_classes = (IsAdminUser,)
    queryset = Apoderado.objects.all()
    serializer_class = ApoderadoRegisterSerializer

    def perform_create(self, serializer):
        email = self.request.data.get('email')
        telefono = self.request.data.get('telefono')

        # Verificar si el teléfono ya está registrado
        if Apoderado.objects.filter(telefono=telefono).exists():
            raise serializers.ValidationError(
                {"details": "El número de teléfono ya está registrado."})

        # Verificar si el correo ya está registrado
        if Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"details": "El correo electrónico ya está registrado."})

        # Generar una contraseña aleatoria
        password = helper.generate_password()
        print(password)
        user = Usuario.objects.create_apoderado(email=email, password=password)
        serializer.save(usuario=user)

        # Preparar la respuesta con el mensaje personalizado
        response_data = serializer.data
        response_data["message"] = "Contraseña enviada al correo"
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        # Autenticación del usuario
        user = authenticate(email=email, password=password)

        if user:
            # Generar tokens de acceso y refresh
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Inicializar el diccionario con los datos comunes
            user_data = {
                'usuario_id': user.id,
                'correo': user.email,
                'rol': 'Invitado',
                'ultima_actualizacion_perfil': user.last_info_updated
            }

            # Si el usuario es apoderado, obtener los datos del apoderado
            if user.is_apoderado:
                try:
                    apoderado = user.apoderado  # Acceso mediante la relación OneToOne
                    user_data['rol'] = 'Apoderado'
                    user_data.update({
                        'id': apoderado.id,
                        'nombres': apoderado.nombres,
                        'apellidos': apoderado.apellidos,
                        'telefono': apoderado.telefono,
                        'direccion': apoderado.direccion
                    })
                except Apoderado.DoesNotExist:
                    pass  # Si no existe el Apoderado, no hacer nada

            # Si el usuario es docente, obtener los datos del docente
            elif user.is_docente:
                try:
                    docente = user.docente  # Acceso mediante la relación OneToOne
                    user_data['rol'] = 'Docente'
                    user_data.update({
                        'id': docente.id,
                        'nombres': docente.nombres,
                        'apellidos': docente.apellidos,
                        'telefono': docente.telefono,
                        'direccion': docente.direccion,
                        'genero': docente.genero.nombre if docente.genero else None,
                        'fecha_nacimiento': docente.fecha_nacimiento,
                        'curso': CursoSerializer(docente.curso).data
                    })
                except Docente.DoesNotExist:
                    pass  # Si no existe el Docente, no hacer nada

            # Si el usuario es administrador, obtener los datos del administrador
            try:
                administrador = user.administrador  # Accede a través de la relación OneToOne
                user_data['rol'] = 'Administrador'
                user_data.update({
                    'id': administrador.id,
                    'nombres': administrador.nombres,
                    'apellidos': administrador.apellidos
                })
            except Administrador.DoesNotExist:
                pass  # Si no es administrador, no hacer nada

            # Retornar el token y los datos del usuario con el rol adecuado
            return Response({
                'refresh_token': str(refresh),
                'access_token': access_token,
                'user': user_data
            })

        return Response({'details': 'Correo o contraseña incorrectos.'}, status=400)
