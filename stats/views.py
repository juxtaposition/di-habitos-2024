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
        habits = Habit.objects.filter(user_id=usuario)

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

    if len(labels) == 1:
        labels.append(labels[0])
        data.append(data[0])

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
            expected_progress = habit.repetitions

            progress_by_date = (
                Habit.objects.filter(id=habit_id)
                .values("created_at__date")
                .annotate(
                    total_repetitions=Sum("repetitions"),
                    current_progress=Sum("current_progress")
                )
                .order_by("created_at__date")
            )

            if progress_by_date.exists():
                progress_labels = [entry["created_at__date"].strftime("%Y-%m-%d") for entry in progress_by_date]
                progress_data = [entry["current_progress"] for entry in progress_by_date]
                total_repetitions = habit.repetitions

            today_progress = Habit.objects.filter(
                user_id=usuario,
                created_at__date=datetime.now().date(),
                id=habit_id
            ).aggregate(today_progress=Sum("current_progress"))['today_progress'] or 0

            today_progress = max(0, today_progress)

            best_progress = Habit.objects.filter(user_id=usuario, id=habit_id).aggregate(best_progress=Max("current_progress"))['best_progress'] or 0
            average_progress = Habit.objects.filter(user_id=usuario, id=habit_id).aggregate(average_progress=Avg("current_progress"))['average_progress'] or 0

        except Habit.DoesNotExist:
            context['error'] = "Hábito no encontrado."

    user_habits = Habit.objects.filter(user_id=usuario)

    habit_data = progress_data
    habit_labels = progress_labels

    daily_average_data = {
        "5h": [1, 1, 2, 2, 3, 3, 3],
        "30m": [0.5, 0.3, 0.4, 0.6, 0.4, 0.6, 1.5],
        "2h": [1, 1.5, 1, 2, 2, 2.5, 2.2],
    }

    # Obtener el progreso acumulado de todos los hábitos día a día
    habits_progress_over_time = (
        Habit.objects.filter(user_id=usuario)
        .values('created_at__date')
        .annotate(total_progress=Sum('current_progress'))
        .order_by('created_at__date')
    )

    all_habits_labels = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in habits_progress_over_time]
    all_habits_data = [entry['total_progress'] for entry in habits_progress_over_time]

    if len(all_habits_labels) == 1:
        all_habits_labels.append(all_habits_labels[0])
        all_habits_data.append(all_habits_data[0])

    # Obtener los datos de progreso de todos los hábitos basados en la fecha de actualización
    all_habits_progress_by_date = (
        Habit.objects.filter(user_id=usuario)
        .values("created_at__date")
        .annotate(
            total_progress=Sum("current_progress"),
            total_repetitions=Sum("repetitions")
        )
        .order_by("created_at__date")
    )

    all_habits_labels = [entry["created_at__date"].strftime("%Y-%m-%d") for entry in all_habits_progress_by_date]
    all_habits_current_data = [entry["total_progress"] for entry in all_habits_progress_by_date]
    all_habits_total_data = [entry["total_repetitions"] for entry in all_habits_progress_by_date]

    context = {
        "byCategory": json.dumps(allCategories),
        "byFrequency": json.dumps(allFrequencies),
        "categories": categories,
        "total_habits_created": total_habits_created,
        "labels": labels, 
        "data": data,
        "daily_average_data": json.dumps(daily_average_data),
        "today_progress": today_progress,
        "best_progress": best_progress,
        "average_progress": average_progress,
        "progress_labels": progress_labels,
        "progress_data": progress_data,
        "total_repetitions": total_repetitions,
        "user_habits": user_habits,  
        "habit_labels": habit_labels,
        "habit_data": habit_data,
        "expected_progress": expected_progress, 
        
        # Nuevas variables para la gráfica de progreso de todos los hábitos
        "all_habits_labels": all_habits_labels,
        "all_habits_current_data": all_habits_current_data,
        "all_habits_total_data": all_habits_total_data,
    }

    return render(request, "stats/index.html", context)
