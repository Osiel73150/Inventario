from django.contrib import admin
from .models import Dispositivo, Ubicacion

@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('numero_activo', 'descripcion', 'marca', 'modelo', 'serie', 'ubicacion')  # ← Se agregó 'ubicacion'
    search_fields = ('numero_activo', 'descripcion', 'marca', 'modelo', 'serie')
    list_filter = ('ubicacion',)  # ← Para filtrar por ubicación en el panel

@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
