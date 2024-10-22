from django.utils.deprecation import MiddlewareMixin
from .models import Usuario


class SetUsersOfflineMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        # Aquí puedes marcar el código como síncrono, ya que solo se ejecuta una vez
        Usuario.objects.all().update(is_online=False)

    def __call__(self, request):
        response = self.get_response(request)
        return response
