from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from alithor.models import Usuario, Diagnostico, EmocionDetectada, Pregunta, Respuesta
from django.db.models import Count
from django.utils.timezone import now
from django.utils import timezone
from transformers import pipeline
from huggingface_hub import login

# Cargar el modelo una sola vez al iniciar el servidor (modelo en español)
# Autenticación con tu token
clasificador = pipeline("text-classification", model="finiteautomata/beto-emotion-analysis")


# Función para analizar emociones en español
def detectar_emocion(texto):
    resultado = clasificador(texto)[0]
    emocion = resultado['label']
    confianza = round(resultado['score'] * 100, 2)

    # Descripción
    descripcion = ""

    # Emociones directamente del modelo sin traducción
    if emocion == "happyness" or emocion == "joy":
        descripcion = "El texto refleja una emoción positiva o regulada."
    elif emocion == "sadness" or emocion == "fear":
        descripcion = "El texto expresa una emoción negativa o desregulada."
    elif emocion == "anger":
        descripcion = "El texto no muestra una emoción dominante."
    else:
        descripcion = "La emoción no se pudo identificar correctamente."

    return emocion, confianza, descripcion



class DashboardView(View):
    def get(self, request, *args, **kwargs):
        nombre = request.session.get('nombre')
        apellido = request.session.get('apellido')
        rol = request.session.get('rol')
        if rol != 'Administrador':
            return JsonResponse({'success': True, 'redirect_url': '/alithor/cuestionarios/'})
        total_pacientes = Usuario.objects.count()
        pacientes_activos = Usuario.objects.filter(status='Activo').count()
        pacientes_inactivos = Usuario.objects.filter(status='Inactivo').count()

        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        pacientes_trastornos = []
        for i in range(1, 7):
            count = Diagnostico.objects.filter(fecha_creado__month=i).count()
            pacientes_trastornos.append(count)

        emociones_reguladas = EmocionDetectada.objects.filter(emocion="Regulada").count()
        emociones_desreguladas = EmocionDetectada.objects.filter(emocion="Desregulada").count()

        context = {
            'nombre': nombre,
            'apellido': apellido,
            'rol': rol,
            'total_pacientes': total_pacientes,
            'pacientes_activos': pacientes_activos,
            'pacientes_inactivos': pacientes_inactivos,
            'meses': meses,
            'pacientes_trastornos': pacientes_trastornos,
            'emociones_reguladas': emociones_reguladas,
            'emociones_desreguladas': emociones_desreguladas,
        }
        return render(request, 'dashboard.html', context)

class UsuariosView(View):
    def get(self, request):
        nombre = request.session.get('nombre')
        apellido = request.session.get('apellido')
        rol = request.session.get('rol')
        if rol != 'Administrador':
            return JsonResponse({'success': True, 'redirect_url': '/alithor/cuestionarios/'})
        usuarios = Usuario.objects.all()
        context = {
            'nombre': nombre,
            'apellido': apellido,
            'rol': rol,
            'usuarios': usuarios,
        }
        return render(request, 'usuarios.html', context)

def agregar_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        numero_empleado = request.POST.get('numero_empleado')
        rol = request.POST.get('rol')
        status = request.POST.get('status') == 'true'

        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            numero_empleado=numero_empleado,
            rol=rol,
            status=status
        )
        usuario.save()

        return JsonResponse({'success': True, 'message': 'Usuario agregado correctamente.'})
    return JsonResponse({'success': False, 'message': 'Método inválido.'})

def actualizar_usuario(request, id):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=id)
        usuario.nombre = request.POST.get('nombre')
        usuario.apellido = request.POST.get('apellido')
        usuario.correo = request.POST.get('correo')
        usuario.numero_empleado = request.POST.get('numero_empleado')
        usuario.rol = request.POST.get('rol')
        usuario.status = request.POST.get('status') == 'true'
        usuario.save()

        return JsonResponse({'success': True, 'message': 'Usuario actualizado correctamente.'})
    return JsonResponse({'success': False, 'message': 'Método inválido.'})

def eliminar_usuario(request, id):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=id)
        usuario.delete()
        return JsonResponse({'success': True, 'message': 'Usuario eliminado correctamente.'})
    return JsonResponse({'success': False, 'message': 'Método inválido.'})

class AnalisisEmocionesView(View):
    def get(self, request):
        respuestas = Respuesta.objects.select_related('usuario', 'pregunta').order_by('-fecha_creado')
        context = {
            'respuestas': respuestas,
        }
        return render(request, 'analisis_emociones.html', context)

class CuestionariosView(View):
    def get(self, request):
        nombre = request.session.get('nombre')
        apellido = request.session.get('apellido')
        rol = request.session.get('rol')
        preguntas = Pregunta.objects.all()
        context = {
            'nombre': nombre,
            'apellido': apellido,
            'rol': rol,
            'preguntas': preguntas,
        }
        return render(request, 'cuestionarios.html', context)

def guardar_respuestas(request):
    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return JsonResponse({'success': False, 'message': 'No se encontró el usuario en sesión.'})

        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El usuario no existe.'})

        respuestas_texto = []

        # Recorrer todas las respuestas
        for key, value in request.POST.items():
            if key.startswith('respuesta_'):
                pregunta_id = key.split('_')[1]
                texto_respuesta = value.strip()

                if not texto_respuesta:
                    continue

                try:
                    pregunta = Pregunta.objects.get(id=pregunta_id)
                except Pregunta.DoesNotExist:
                    continue

                # Verificar si la respuesta ya existe
                respuesta, created = Respuesta.objects.get_or_create(
                    usuario=usuario,
                    pregunta=pregunta,
                    texto_respuesta=texto_respuesta,
                    defaults={'fecha_creado': timezone.now()}
                )

                respuestas_texto.append(texto_respuesta)

                # Analizar emoción para esta respuesta
                emocion_detectada, confianza, descripcion = detectar_emocion(texto_respuesta)

                # Crear Diagnóstico para cada respuesta (si no existe ya)
                diagnostico, created = Diagnostico.objects.get_or_create(
                    usuario=usuario,
                    fecha_creado=now(),
                    defaults={'descripcion': descripcion}
                )

                # Guardar emoción detectada relacionada al diagnóstico y la respuesta
                EmocionDetectada.objects.create(
                    respuesta=respuesta,
                    diagnostico=diagnostico,
                    emocion=emocion_detectada,
                    nivel_confianza=confianza,
                    descripcion=descripcion,
                    creado_en=now()
                )

        return JsonResponse({'success': True, 'message': 'Análisis emocional completado y guardado correctamente.'})

    return JsonResponse({'success': False, 'message': 'Método inválido.'})

def analizar_emocion(request, respuesta_id):
    respuesta = get_object_or_404(Respuesta, id=respuesta_id)
    texto_respuesta = respuesta.texto_respuesta

    emocion_detectada, confianza = detectar_emocion(texto_respuesta)

    emocion = EmocionDetectada(
        respuesta=respuesta,
        emocion=emocion_detectada,
        nivel_confianza=confianza,
        creado_en=now()
    )
    emocion.save()

    return JsonResponse({
        'success': True,
        'emocion': emocion_detectada,
        'confianza': confianza
    })


def guardar_analisis_emocional(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('respuesta_'):
                respuesta_id = key.split('_')[1]
                try:
                    respuesta = Respuesta.objects.get(id=respuesta_id)
                    
                    # Evita guardar duplicados
                    if not EmocionDetectada.objects.filter(respuesta=respuesta).exists():
                        emocion_detectada, confianza = detectar_emocion(respuesta.texto_respuesta)
                        emocion = EmocionDetectada(
                            respuesta=respuesta,
                            emocion=emocion_detectada,
                            nivel_confianza=confianza,
                            creado_en=now()
                        )
                        emocion.save()
                except Respuesta.DoesNotExist:
                    continue

        return JsonResponse({'success': True, 'message': 'Análisis emocional completado y guardado correctamente.'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

