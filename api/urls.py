from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from api import views

router = routers.DefaultRouter()

router.register(r'categorias', views.CategoriaView, basename='categorias')
router.register(r'generos', views.GeneroView, basename='generos')
router.register(r'niveles', views.NivelView, basename='niveles')
router.register(r'cursos', views.CursoView, basename='cursos')
router.register(r'asistencias', views.AsistenciaViewSet, basename='asistencias')
router.register(r'estados/asistencia', views.EstadoAsistenciaView, basename='estados_asistencia')
router.register(r'tareas', views.TareaView, basename='tareas')
router.register(r'estados/tarea', views.EstadoTareaView, basename='estados_tarea')
router.register(r'noticias', views.NoticiaView, basename='noticias')
router.register(r'apoderados', views.ApoderadoView, basename='apoderados')
router.register(r'estudiantes', views.EstudianteView, basename='estudiantes')
router.register(r'docentes', views.DocenteView, basename='docentes')
router.register(r'aulas', views.AulaView, basename='aulas')
router.register(r'calificaciones', views.CalificacionView, basename='calificaciones')
router.register(r'conversaciones', views.ConversacionView, basename='conversaciones')
router.register(r'mensajes', views.MensajeView, basename='mensajes')
router.register(r'imagenes', views.ImagenView, basename='imagenes')

urlpatterns = [
    path('api/v1/aulas/docente/<int:pk>/', views.AulasPorDocenteView.as_view({'get': 'retrieve'}), name='aulas_por_docente'),
    path('api/v1/estudiantes/apoderado/<int:pk>/', views.EstudiantesPorApoderadoView.as_view({'get': 'retrieve'}), name='estudiantes_por_apoderado'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('registro/docente', views.RegisterDocenteView.as_view(), name='registro_docente'),
    path('registro/apoderado', views.RegisterApoderadoView.as_view(), name='registro_apoderado'),

    # Incluir todas las rutas de los viewsets
    path('api/v1/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)