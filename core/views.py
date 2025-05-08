from django.views.generic import View
from django.shortcuts import render,redirect
from django.http import JsonResponse
from alithor.models import Usuario

class HomeView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Buscar usuario por correo
            usuario = Usuario.objects.get(correo=username)
            if usuario.contrasena == password:
                # Guardar datos en sesión
                request.session['usuario_id'] = usuario.id
                request.session['correo'] = usuario.correo
                request.session['nombre'] = usuario.nombre
                request.session['apellido'] = usuario.apellido
                request.session['rol'] = usuario.rol
                request.session['status'] = usuario.status

                return JsonResponse({'success': True, 'redirect_url': '/alithor/'})
            else:
                return JsonResponse({'success': False, 'error': 'Contraseña incorrecta'})
        except Usuario.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})
