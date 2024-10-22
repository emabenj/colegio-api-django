import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.db import transaction
from .helper_functions import BHelperFunctions as helper
from .models import Apoderado, Docente, AulaCurso, Estudiante, AulaCurso, Usuario



class ChatConsumer(AsyncWebsocketConsumer):
    TYPE_CHAT_MESSAGE = "chat_message"
    TYPE_RECENT_MESSAGE = "recent_message"
    async def connect(self):
        # Obtener los IDs de los usuarios desde la URL
        # self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.user1_id = self.scope['url_route']['kwargs']['user1_id']
        self.user2_id = self.scope['url_route']['kwargs']['user2_id']

        self.room_group_name = f'chat_{self.user1_id}_{self.user2_id}'

        # Obtener el token de la cabecera o URL
        token = self.scope['query_string'].decode().split('=')[1]
        user = await helper.authenticate_user(token)
        # print(user)

        if user:
            # Agregar al grupo basado en la conversación
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        else:
            print("RECHAZADO")
            await self.close(code=4001)

    async def disconnect(self, close_code):
        # Eliminar al usuario del grupo de la conversación
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        type_data = data.get('type')
        message_data = data.get('message')            

        if message_data:
            # Transmitir el mensaje a ambos usuarios en la conversación o solo en la lista de chats recientes
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': type_data,
                    'message': message_data
                }
            )

    async def chat_message(self, event):
        message = event['message']

        # Enviar el mensaje al WebSocket
        await self.send(text_data=json.dumps(
            {
                'type': self.TYPE_CHAT_MESSAGE,
                'message': message
            }
        ))
    async def recent_message(self, event):
        message = event['message']

        # Enviar el mensaje al WebSocket
        await self.send(text_data=json.dumps(
            {
                'type': self.TYPE_RECENT_MESSAGE,
                'message': message
            }
        ))


class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Obtener el token del query string
        token = self.scope['query_string'].decode().split('=')[1]
        user = await helper.authenticate_user(token)

        if user:
            self.aula_id = self.scope['url_route']['kwargs']['aula_id']
            self.user = user

            # Definir el nombre del grupo según el aula_id
            self.group_name = f'online_aula_{self.aula_id}'

            # Añadir al grupo de usuarios en línea
            await self.add_to_online_group()

            # Aceptar la conexión WebSocket
            await self.accept()

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': f'user_connected',
                    'user_id': self.user.id,
                }
            )

            # Enviar la lista de usuarios en línea según el rol
            await self.send_online_users()

        else:
            await self.close()

    async def disconnect(self, close_code):
        # Quitar al usuario del grupo cuando se desconecta
        await self.remove_from_online_group()

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': f'user_disconnected',
                'user_id': self.user.id,
            }
        )

    async def receive(self, text_data):
        pass

    async def user_connected(self, event):
        """Manejador del mensaje 'user_connected'"""
        user_id = event['user_id']
        await self.send_user_accion(user_id, True)

    async def user_disconnected(self, event):
        """Manejador del mensaje 'user_disconnected'"""
        user_id = event['user_id']
        await self.send_user_accion(user_id, False)

    async def send_user_accion(self, user_id, accion):
        """Envía un mensaje indicando el estado de conexión del usuario y actualiza su estado en la BD"""
        accion_str = 'connected' if accion else 'disconnected'
        # Añadir log para verificar que se ejecuta correctamente

        # Actualiza los campos is_online y last_connection en la base de datos
        await self.update_user_status(user_id, accion)

        await self.send(text_data=json.dumps({
            'type': f'user_{accion_str}',
            'user_id': user_id,
        }))

    # @database_sync_to_async
    # def authenticate_user(self, token):
    #     from rest_framework_simplejwt.authentication import JWTAuthentication
    #     """Autentica el usuario a través del token"""
    #     try:
    #         validated_token = JWTAuthentication().get_validated_token(token)
    #         user_id = validated_token['user_id']
    #         return Usuario.objects.get(id=user_id)
    #     except Exception:
    #         return None

    @database_sync_to_async
    def update_user_status(self, user_id, accion):
        """Actualiza el estado de conexión y última conexión del usuario en la base de datos"""
        try:
            with transaction.atomic():
                usuario = Usuario.objects.get(pk=user_id)
                usuario.is_online = accion
                if accion:  # Si se conecta
                    usuario.last_connection = timezone.now()
                usuario.save()
        except Usuario.DoesNotExist:
            # Manejar el caso si el usuario no existe
            print(f"Usuario con ID {user_id} no encontrado")

    async def add_to_online_group(self):
        """Añade al usuario al grupo de usuarios en línea según su rol"""
        if self.group_name:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

    async def remove_from_online_group(self):
        """Quita al usuario del grupo de usuarios en línea"""
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_online_users(self):
        """Envía la lista de usuarios en línea filtrada según el rol del usuario"""
        # Obtener los usuarios en línea del aula correspondiente
        online_users = await self.get_online_users()

        filtered_users = [user.usuario.id for user in online_users]

        # Enviar la lista de usuarios en línea
        await self.send(text_data=json.dumps({
            'type': f'{self.group_name}',
            'users_online': filtered_users
        }))

    @database_sync_to_async
    def get_online_users(self):
        """Obtiene los usuarios en línea para el aula especificada"""
        return self.filter_users_by_aula_and_online_status()

    def filter_users_by_aula_and_online_status(self):
        """Filtra usuarios por aula y estado de conexión"""
        # Obtener el ID del aula del group_name
        aula_id = self.group_name.split("_")[-1]

        # Obtener usuarios en línea que pertenezcan al aula, según el rol
        users_en_linea = Apoderado.objects.filter(
            usuario__is_online=True,
            estudiantes__aula__id=aula_id
        ).select_related('usuario') if self.user.is_docente else Docente.objects.filter(
            usuario__is_online=True,
            aulacurso__aula__id=aula_id
        ).select_related('usuario') if self.user.is_apoderado else []
        return list(users_en_linea)
