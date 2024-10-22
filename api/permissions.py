from rest_framework import permissions


class ReadOnlyForAll(permissions.BasePermission):
    def has_permission(self, request, view):
        # Todos pueden leer
        if request.method in permissions.SAFE_METHODS:
            return True
        # Solo el admin puede editar (POST, PUT, DELETE)
        return request.user.is_staff


class ReadOnlyForDocente(permissions.BasePermission):
    def has_permission(self, request, view):
        # Verifica que el usuario esté autenticado
        if not request.user.is_authenticated:
            return False
        # Todos pueden leer (GET)
        if request.method in permissions.SAFE_METHODS:
            # Permite el acceso si es docente o admin
            return request.user.is_docente or request.user.is_staff
        # Solo el admin puede editar (POST, PUT, DELETE)
        return request.user.is_staff


class ReadOnlyForApoderado(permissions.BasePermission):
    def has_permission(self, request, view):
        # Verifica que el usuario esté autenticado
        if not request.user.is_authenticated:
            return False
        # Todos pueden leer (GET)
        if request.method in permissions.SAFE_METHODS:
            # Permite el acceso si es apoderado o admin
            return request.user.is_apoderado or request.user.is_staff
        # Solo el admin puede editar (POST, PUT, DELETE)
        return request.user.is_staff


class DocenteAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Verifica que el usuario esté autenticado
        if not request.user.is_authenticated:
            return False
        # Todos pueden leer (GET)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Permite cualquier acción si es docente o admin
        return request.user.is_docente or request.user.is_staff


class DocenteApoderadoPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Verifica que el usuario esté autenticado
        if not request.user.is_authenticated:
            return False
        # Todos pueden leer (GET)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Permite cualquier acción si es apoderado o docente
        return request.user.is_apoderado or request.user.is_docente


class ControlApoderadoPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Verifica que el usuario esté autenticado
        if not request.user.is_authenticated:
            return False
        # Solo el apoderado puede ver o editar
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_apoderado
        # Permitir editar solo si es apoderado
        return request.user.is_apoderado


class ControlDocentePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Verifica que el usuario esté autenticado
        if not request.user.is_authenticated:
            return False
        # Solo el docente puede ver o editar
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_docente
        # Permitir editar solo si es docente
        return request.user.is_docente
