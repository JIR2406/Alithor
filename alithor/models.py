from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField()

    def __str__(self):
        return self.title


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    numero_empleado = models.CharField(max_length=20)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    rol = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Diagnostico(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_creado = models.DateTimeField(auto_now_add=True)

class Pregunta(models.Model):
    texto_pregunta = models.TextField()
    tipo_pregunta = models.CharField(max_length=50, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

class Respuesta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    texto_respuesta = models.TextField()
    fecha_creado = models.DateTimeField(auto_now_add=True)

class EmocionDetectada(models.Model):
    respuesta = models.ForeignKey(Respuesta, on_delete=models.CASCADE)
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.SET_NULL, null=True, blank=True)  # NUEVO
    emocion = models.CharField(max_length=50)
    nivel_confianza = models.FloatField()
    descripcion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
