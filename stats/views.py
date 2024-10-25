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
    categories = Category.objects.all()
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    category_id = request.GET.get("category")
    frequency = request.GET.get("frequency")
    habit_id = request.GET.get("habit_id")

    habits = Habit.objects.filter(user_id=usuario)

    # Filtrar por rango de fechas si se proporcionan ambas fechas
    if start_date and end_date:
        try:
            start_date_parsed = parse_date(start_date)
            end_date_parsed = parse_date(end_date)
            if start_date_parsed and end_date_parsed:
                habits = habits.filter(created_at__date__gte=start_date_parsed, created_at__date__lte=end_date_parsed)
        except ValueError:
            context['error'] = "Formato de fecha inválido."

    # Filtrar por categoría si se proporciona
    if category_id:
        habits = habits.filter(category_id=category_id)

    # Filtrar por frecuencia si se especifica
    if frequency:
        habits = habits.filter(frequency=frequency)

    category_names = habits.values_list("category__name", flat=True)
    freq_names = habits.values_list("frequency", flat=True)
    allCategories = dict(Counter(category_names))
    allFrequencies = dict(Counter(freq_names))
    total_habits_created = habits.count()

    # Gráfica de hábitos creados por fecha
    habits_by_date = (
        habits.values("created_at__date")
        .annotate(count=Count("id"))
        .order_by("created_at__date")
    )
    labels = [habit["created_at__date"].strftime("%Y-%m-%d") for habit in habits_by_date]
    data = [habit["count"] for habit in habits_by_date]

    if len(labels) == 1:
        labels.append(labels[0])
        data.append(data[0])

    # Variables para progreso
    progress_labels = []
    progress_data = []
    total_repetitions = 0
    expected_progress = 0
    today_progress = 0
    best_progress = 0
    average_progress = 0

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

    # Progreso acumulado de todos los hábitos
    habits_progress_over_time = (
        habits
        .values('created_at__date')
        .annotate(total_progress=Sum('current_progress'))
        .order_by('created_at__date')
    )

    all_habits_labels = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in habits_progress_over_time]
    all_habits_data = [entry['total_progress'] for entry in habits_progress_over_time]

    if len(all_habits_labels) == 1:
        all_habits_labels.append(all_habits_labels[0])
        all_habits_data.append(all_habits_data[0])

    # Progreso de todos los hábitos por fecha de actualización
    all_habits_progress_by_date = (
        habits
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

    completion_labels = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in all_habits_progress_by_date]
    completion_percentage_data = [
        (entry['total_progress'] / entry['total_repetitions']) * 100 if entry['total_repetitions'] > 0 else 0
        for entry in all_habits_progress_by_date
    ]

    if len(completion_labels) == 1:
        completion_labels.append(completion_labels[0])
        completion_percentage_data.append(completion_percentage_data[0])

    frequency_counter = dict(Counter(freq_names))
    frequency_labels = list(frequency_counter.keys())
    frequency_data = list(frequency_counter.values())

    habit_names = habits.values_list('name', flat=True)
    habit_repetitions = habits.values_list('repetitions', flat=True)

    context = {
        "byCategory": json.dumps(allCategories),
        "byFrequency": json.dumps(allFrequencies),
        "categories": categories,
        "total_habits_created": total_habits_created,
        "labels": labels, 
        "data": data,
        "today_progress": today_progress,
        "best_progress": best_progress,
        "average_progress": average_progress,
        "progress_labels": progress_labels,
        "progress_data": progress_data,
        "total_repetitions": total_repetitions,
        "user_habits": Habit.objects.filter(user_id=usuario),  
        "habit_labels": progress_labels,
        "habit_data": progress_data,
        "expected_progress": expected_progress, 
        "all_habits_labels": all_habits_labels,
        "all_habits_current_data": all_habits_current_data,
        "all_habits_total_data": all_habits_total_data,
        "completion_labels": completion_labels,
        "completion_percentage_data": completion_percentage_data,
        "frequency_counter": json.dumps(frequency_counter),
        "frequency_labels": json.dumps(frequency_labels),
        "frequency_data": json.dumps(frequency_data),
        "habit_names": json.dumps(list(habit_names)),
        "habit_repetitions": json.dumps(list(habit_repetitions)),
    }

    return render(request, "stats/index.html", context)
