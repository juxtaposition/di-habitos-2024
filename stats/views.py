from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from habit.models import Habit, Category
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count, Q, Max, Avg
import json
from collections import Counter
from datetime import datetime

@login_required
def estadisticas(request):
    usuario = request.user
    # Obtener categorías
    categories = Category.objects.all()

    # Obtener los filtros de fecha, categoría y frecuencia desde el formulario
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    category_id = request.GET.get("category")
    frequency = request.GET.get("frequency")
    habit_id = request.GET.get("habit_id")

    # Inicializar queryset de hábitos
    habits = Habit.objects.filter(user_id=usuario)

    # Si no hay fechas proporcionadas, usar todos los hábitos
    if not start_date or not end_date:
        habits = Habit.objects.filter(user_id=usuario)  # No filtrar por rango de fechas

    # Si se proporcionan fechas, aplicar el filtrado por rango de fechas
    if start_date and end_date:
        try:
            start_date_parsed = parse_date(start_date)
            end_date_parsed = parse_date(end_date)
            if start_date_parsed and end_date_parsed:
                habits = habits.filter(created_at__range=[start_date_parsed, end_date_parsed])
        except ValueError:
            context['error'] = "Formato de fecha inválido."

    # Filtrar los hábitos por categoría si se especifica
    if category_id:
        habits = habits.filter(category_id=category_id)
    if frequency:
        habits = habits.filter(frequency=frequency)

    # Obtener los nombres de las categorías y frecuencias
    category_names = habits.values_list("category__name", flat=True)
    freq_names = habits.values_list("frequency", flat=True)

    # Contar hábitos por categoría y frecuencia
    allCategories = dict(Counter(category_names))
    allFrequencies = dict(Counter(freq_names))

    # Obtener el conteo total de hábitos creados
    total_habits_created = habits.count()

    # Obtener datos para la gráfica de hábitos creados por fecha (después de aplicar filtros)
    habits_by_date = (
        habits.values("created_at__date")
        .annotate(count=Count("id"))
        .order_by("created_at__date")
    )

    # Definir variables separadas para labels y data
    labels = [habit["created_at__date"].strftime("%Y-%m-%d") for habit in habits_by_date]
    data = [habit["count"] for habit in habits_by_date]

    # Si sólo hay un día en el filtro, duplicarlo para que se visualice correctamente
    if len(labels) == 1:
        labels.append(labels[0])  # Duplicar la misma fecha
        data.append(data[0])  # Duplicar el mismo valor

    # Inicializamos variables para progreso
    progress_labels = []
    progress_data = []
    total_repetitions = 0
    expected_progress = 0
    today_progress = 0
    best_progress = 0
    average_progress = 0
    
    # Si se especifica un hábito, obtener los datos de progreso
    if habit_id:
        try:
            habit = Habit.objects.get(id=habit_id, user_id=usuario)

            # Obtener el progreso final esperado
            expected_progress = habit.repetitions  # Progreso final esperado

            # Obtener los datos del progreso del hábito seleccionado
            progress_by_date = (
                Habit.objects.filter(id=habit_id)
                .values("created_at__date")
                .annotate(
                    total_repetitions=Sum("repetitions"),
                    current_progress=Sum("current_progress")
                )
                .order_by("created_at__date")
            )

            # Preparar los datos para la gráfica si existen resultados
            if progress_by_date.exists():
                progress_labels = [entry["created_at__date"].strftime("%Y-%m-%d") for entry in progress_by_date]
                progress_data = [entry["current_progress"] for entry in progress_by_date]
                total_repetitions = habit.repetitions

            # Calcular los progresos hoy, mejor y promedio solo para el hábito específico
            today_progress = Habit.objects.filter(
                user_id=usuario,
                created_at__date=datetime.now().date(),
                id=habit_id
            ).aggregate(today_progress=Sum("current_progress"))['today_progress'] or 0

            # Asegúrate de que today_progress no sea negativo
            today_progress = max(0, today_progress)

            best_progress = Habit.objects.filter(user_id=usuario, id=habit_id).aggregate(best_progress=Max("current_progress"))['best_progress'] or 0
            average_progress = Habit.objects.filter(user_id=usuario, id=habit_id).aggregate(average_progress=Avg("current_progress"))['average_progress'] or 0

        except Habit.DoesNotExist:
            context['error'] = "Hábito no encontrado."

    # Obtener todos los hábitos del usuario para el formulario
    user_habits = Habit.objects.filter(user_id=usuario)

    # Cambia la variable de datos para el gráfico del hábito específico
    habit_data = progress_data  # Usar los datos de progreso obtenidos de la base de datos
    habit_labels = progress_labels  # Usar las etiquetas obtenidas de la base de datos

    # Simular datos para otras gráficas si es necesario (pero basados en el queryset filtrado si es posible)
    water_data = [2.0, 2.1, 2.3, 2.0, 2.4, 2.5, 2.2]
    daily_average_data = {
        "5h": [1, 1, 2, 2, 3, 3, 3],
        "30m": [0.5, 0.3, 0.4, 0.6, 0.4, 0.6, 1.5],
        "2h": [1, 1.5, 1, 2, 2, 2.5, 2.2],
    }
    grafico1_data = [70, 30]
    grafico2_data = [50, 50]
    grafico3_data = [10, 20, 15, 25, 30, 40]
    grafico4_data = [20, 30, 25, 35, 40, 45]

    # Contexto para el template
    context = {
        "byCategory": json.dumps(allCategories),
        "byFrequency": json.dumps(allFrequencies),
        "categories": categories,
        "total_habits_created": total_habits_created,
        "labels": labels, 
        "data": data,
        "water_data": json.dumps(water_data),
        "daily_average_data": json.dumps(daily_average_data),
        "grafico1_data": json.dumps(grafico1_data),
        "grafico2_data": json.dumps(grafico2_data),
        "grafico3_data": json.dumps(grafico3_data),
        "grafico4_data": json.dumps(grafico4_data),
        "today_progress": today_progress,
        "best_progress": best_progress,
        "average_progress": average_progress,
        "progress_labels": progress_labels,
        "progress_data": progress_data,
        "total_repetitions": total_repetitions,
        "user_habits": user_habits,  # Agregar user_habits al contexto
        "habit_labels": habit_labels,
        "habit_data": habit_data,
        "expected_progress": expected_progress, 
    }

    return render(request, "stats/index.html", context)
