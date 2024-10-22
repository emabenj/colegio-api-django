import random
import string

from channels.db import database_sync_to_async
from .models import Usuario


class BHelperFunctions:
    @staticmethod
    def generate_password(length=12):
        """Genera una contraseña aleatoria de una longitud especificada.

        Args:
            length (int): La longitud de la contraseña a generar.

        Returns:
            str: La contraseña generada.
        """
        # Definir los caracteres que se usarán en la contraseña
        characters = string.ascii_letters + string.digits
        
        # Generar una contraseña aleatoria
        password = ''.join(random.choice(characters) for _ in range(length))
        
        return password
    
    @database_sync_to_async
    def authenticate_user(self, token):
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework_simplejwt.exceptions import InvalidToken
        """Autentica el usuario a través del token"""
        try:
            validated_token = JWTAuthentication().get_validated_token(token)
            user_id = validated_token['user_id']
            return Usuario.objects.get(id=user_id)
        except InvalidToken:
            return None  # Token no es válido
        except Usuario.DoesNotExist:
            return None  # Usuario no existe
        except Exception as e:
            # Manejar cualquier otro error inesperado
            return None