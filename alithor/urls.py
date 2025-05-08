from django.urls import path
from . import views
from django.contrib import admin

app_name = 'alithor'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('admin/', admin.site.urls),
    path('usuarios/', views.UsuariosView.as_view(), name='usuarios'),
    path('usuarios/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('usuarios/actualizar/<int:id>/', views.actualizar_usuario, name='actualizar_usuario'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('analisis_emociones/', views.AnalisisEmocionesView.as_view(), name='analisis_emociones'),
    path('cuestionarios/', views.CuestionariosView.as_view(), name='cuestionarios'),  
    path('cuestionarios/guardar/', views.guardar_respuestas, name='guardar_respuestas'),  
    path('emociones/analizar/<int:respuesta_id>/', views.analizar_emocion, name='analizar_emocion'),
    path('cuestionarios/guardar/', views.guardar_analisis_emocional, name='guardar_analisis_emocional'),

]
