from django.contrib import admin
from .models import Usuario, Diagnostico, Pregunta, Respuesta, EmocionDetectada

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'numero_empleado', 'correo', 'rol', 'status')
    search_fields = ('nombre', 'apellido', 'correo', 'rol', 'status')
    list_filter = ('rol', 'status')

@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'descripcion', 'fecha_creado')
    search_fields = ('descripcion',)
    list_filter = ('fecha_creado',)

@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ('texto_pregunta', 'tipo_pregunta', 'creado_en')
    search_fields = ('texto_pregunta',)
    list_filter = ('tipo_pregunta',)

@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pregunta', 'texto_respuesta', 'fecha_creado')
    search_fields = ('texto_respuesta',)
    list_filter = ('fecha_creado',)

@admin.register(EmocionDetectada)
class EmocionDetectadaAdmin(admin.ModelAdmin):
    list_display = ('respuesta', 'emocion', 'nivel_confianza', 'creado_en')
    search_fields = ('emocion',)
    list_filter = ('emocion',)
