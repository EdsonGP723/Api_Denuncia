from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Denuncia(models.Model):
    TIPOS_INCIDENTE = [
        ('fraud', 'Fraude'),
        ('harassment', 'Acoso'),
        ('discrimination', 'Discriminación'),
        ('corruption', 'Corrupción'),
        ('safety', 'Seguridad'),
        ('other', 'Otro'),
    ]

    CANALES = [
        ('web', 'Web'),
        ('email', 'Email'),
        ('phone', 'Teléfono'),
        ('presencial', 'Presencial'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    anonimo = models.BooleanField(default=True)
    canal = models.CharField(max_length=20, choices=CANALES, default='web')

    # Datos del denunciante
    relacion_empresa = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, default='México')

    # Datos del denunciado
    nombre_denunciado = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255, blank=True)
    departamento = models.CharField(max_length=255, blank=True)

    # Incidente
    tipo_incidente = models.CharField(max_length=50, choices=TIPOS_INCIDENTE)
    descripcion = models.TextField()
    fecha_aproximada = models.CharField(max_length=100, blank=True)
    es_continuo = models.BooleanField(default=False)

    # Ubicación
    ciudad = models.CharField(max_length=255, blank=True)
    relacionado_trabajo = models.BooleanField(default=True)

    # Evidencia
    tiene_evidencia = models.BooleanField(default=False)
    descripcion_evidencia = models.TextField(blank=True)

    # Datos generados por IA
    datos_json = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Denuncia #{self.id} - {self.tipo_incidente} - {self.fecha_creacion.strftime('%Y-%m-%d')}"
