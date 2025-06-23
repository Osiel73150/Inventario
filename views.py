from django.shortcuts import render, get_object_or_404, redirect
from .models import Dispositivo, Ubicacion, MovimientoDispositivo
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

def lista_dispositivos(request):
    query = request.GET.get('q')
    dispositivos = Dispositivo.objects.all()

    if query:
        dispositivos = dispositivos.filter(
            Q(numero_activo__icontains=query) |
            Q(serie__icontains=query)
        )

    return render(request, 'equipos/lista_dispositivos.html', {
        'dispositivos': dispositivos,
        'query': query
    })

def detalle_dispositivo(request, numero_activo):
    dispositivo = get_object_or_404(Dispositivo, numero_activo=numero_activo)
    
    # Obtener los últimos 5 movimientos
    ultimos_movimientos = MovimientoDispositivo.objects.filter(
        dispositivo=dispositivo
    ).select_related(
        'usuario', 
        'ubicacion_anterior', 
        'ubicacion_nueva',
        'responsable_anterior', 
        'responsable_nuevo'
    ).order_by('-fecha')[:5]
    
    return render(request, 'equipos/detalle_dispositivo.html', {
        'dispositivo': dispositivo,
        'ultimos_movimientos': ultimos_movimientos,
    })

@login_required
def editar_dispositivo(request, pk):
    dispositivo = get_object_or_404(Dispositivo, pk=pk)
    ubicaciones = Ubicacion.objects.all()
    usuarios = User.objects.all()
    
    # Guardar valores anteriores
    ubicacion_anterior = dispositivo.ubicacion
    responsable_anterior = dispositivo.responsable

    if request.method == 'POST':
        # Guardar ubicación
        ubicacion_id = request.POST.get('ubicacion')
        nueva_ubicacion = Ubicacion.objects.get(id=ubicacion_id) if ubicacion_id else None

        # Guardar responsable
        responsable_id = request.POST.get('responsable')
        nuevo_responsable = User.objects.get(id=responsable_id) if responsable_id else None

        # Verificar si hubo cambios
        cambio_ubicacion = nueva_ubicacion != dispositivo.ubicacion
        cambio_responsable = nuevo_responsable != dispositivo.responsable

        # Solo crear movimiento si hay cambios
        if cambio_ubicacion or cambio_responsable:
            MovimientoDispositivo.objects.create(
                dispositivo=dispositivo,
                ubicacion_anterior=ubicacion_anterior,
                ubicacion_nueva=nueva_ubicacion,
                responsable_anterior=responsable_anterior,
                responsable_nuevo=nuevo_responsable,
                usuario=request.user
            )

        # Actualizar el dispositivo
        dispositivo.ubicacion = nueva_ubicacion
        dispositivo.responsable = nuevo_responsable
        dispositivo.save()

        return redirect('lista_dispositivos')

    return render(request, 'equipos/editar_dispositivo.html', {
        'dispositivo': dispositivo,
        'ubicaciones': ubicaciones,
        'usuarios': usuarios
    })

def dispositivos_por_ubicacion(request, ubicacion_id):
    ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id)
    dispositivos = Dispositivo.objects.filter(ubicacion=ubicacion)
    return render(request, 'equipos/dispositivos_por_ubicacion.html', {
        'ubicacion': ubicacion,
        'dispositivos': dispositivos
    })

@login_required
def sin_asignar(request):
    # Obtener los parámetros de los checkboxes
    sin_ubicacion = request.GET.get('sin_ubicacion')
    sin_responsable = request.GET.get('sin_responsable')
    
    dispositivos = Dispositivo.objects.all()

    # Aplicar filtros basados en los checkboxes
    if sin_ubicacion and sin_responsable:
        # Ambos checkboxes marcados
        dispositivos = dispositivos.filter(responsable__isnull=True, ubicacion__isnull=True)
    elif sin_ubicacion:
        # Solo sin ubicación
        dispositivos = dispositivos.filter(ubicacion__isnull=True)
    elif sin_responsable:
        # Solo sin responsable
        dispositivos = dispositivos.filter(responsable__isnull=True)
    else:
        # Si no hay filtros, mostrar todos los que tengan al menos uno sin asignar
        dispositivos = dispositivos.filter(Q(responsable__isnull=True) | Q(ubicacion__isnull=True))
    
    ubicaciones = Ubicacion.objects.all()
    responsables = User.objects.all()

    if request.method == 'POST':
        seleccionados = request.POST.getlist('dispositivos')
        nueva_ubicacion_id = request.POST.get('ubicacion')
        nuevo_responsable_id = request.POST.get('responsable')

        nueva_ubicacion = Ubicacion.objects.get(id=nueva_ubicacion_id) if nueva_ubicacion_id else None
        nuevo_responsable = User.objects.get(id=nuevo_responsable_id) if nuevo_responsable_id else None

        for id_disp in seleccionados:
            dispositivo = Dispositivo.objects.get(id=id_disp)
            
            # Guardar valores anteriores
            ubicacion_anterior = dispositivo.ubicacion
            responsable_anterior = dispositivo.responsable
            
            # Verificar si hay cambios
            cambio_ubicacion = nueva_ubicacion and nueva_ubicacion != dispositivo.ubicacion
            cambio_responsable = nuevo_responsable and nuevo_responsable != dispositivo.responsable
            
            # Registrar movimiento si hay cambios
            if cambio_ubicacion or cambio_responsable:
                MovimientoDispositivo.objects.create(
                    dispositivo=dispositivo,
                    ubicacion_anterior=ubicacion_anterior if cambio_ubicacion else None,
                    ubicacion_nueva=nueva_ubicacion if cambio_ubicacion else None,
                    responsable_anterior=responsable_anterior if cambio_responsable else None,
                    responsable_nuevo=nuevo_responsable if cambio_responsable else None,
                    usuario=request.user
                )
            
            # Actualizar dispositivo
            if nueva_ubicacion:
                dispositivo.ubicacion = nueva_ubicacion
            if nuevo_responsable:
                dispositivo.responsable = nuevo_responsable
            dispositivo.save()

        messages.success(request, "Asignación realizada correctamente.")
        return redirect('sin_asignar')

    return render(request, 'equipos/sin_asignar.html', {
        'dispositivos': dispositivos,
        'ubicaciones': ubicaciones,
        'responsables': responsables,
        'sin_ubicacion': sin_ubicacion,
        'sin_responsable': sin_responsable
    })
