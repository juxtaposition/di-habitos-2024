from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from habit.models import Habit, Category
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count, Max, Avg
import json
from collections import Counter
from datetime import datetime, timedelta

@login_required
def estadisticas(request):
    usuario = request.user
    context = {}
    
    categories = Category.objects.all()
    
    # Obtener parámetros de filtro de la URL
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    category_id = request.GET.get("category")
    frequency = request.GET.get("frequency")
    habit_id = request.GET.get("habit_id")

    habits = Habit.objects.filter(user_id=usuario)

    filters_applied = False

    # Aplicar filtros de fecha de inicio y fin si están presentes
    if start_date and end_date:
        try:
            start_date_parsed = parse_date(start_date)
            end_date_parsed = parse_date(end_date)
            if start_date_parsed and end_date_parsed:
                habits = habits.filter(
                    created_at__date__gte=start_date_parsed,
                    created_at__date__lte=end_date_parsed
                )
                filters_applied = True
        except ValueError:
            context['error'] = "Las fechas tienen un formato inválido."

    # Filtrar por categoría si se seleccionó alguna
    if category_id:
        habits = habits.filter(category_id=category_id)
        filters_applied = True

    # Filtrar por frecuencia si está especificada
    if frequency:
        habits = habits.filter(frequency=frequency)
        filters_applied = True

    # Mostrar mensaje si no hay datos después de aplicar los filtros
    if filters_applied and not habits.exists():
        context['no_data_message'] = "No se encontraron datos para los filtros aplicados."

    # Contar ocurrencias de categorías y frecuencias en los hábitos
    category_names = habits.values_list("category__name", flat=True)
    freq_names = habits.values_list("frequency", flat=True)
    allCategories = dict(Counter(category_names))
    allFrequencies = dict(Counter(freq_names))
    total_habits_created = habits.count()

    # Contar hábitos creados por fecha para el gráfico
    habits_by_date = (
        habits.values("created_at__date")
        .annotate(count=Count("id"))
        .order_by("created_at__date")
    )
    
    # Extraer etiquetas y datos para la gráfica
    labels_createdHabits = [habit["created_at__date"].strftime("%Y-%m-%d") for habit in habits_by_date]
    data_createdHabits = [habit["count"] for habit in habits_by_date]

    if len(labels_createdHabits) == 1:
        labels_createdHabits.append(labels_createdHabits[0])
        data_createdHabits.append(data_createdHabits[0])

    # Variables para almacenar el progreso de un hábito específico
    progress_labels = []
    progress_data = []
    total_specificHabit = 0
    expected_progress = 0
    best_progress = 0

    # Obtener y procesar datos para un hábito específico si se selecciona
    if habit_id:
        try:
            habit = Habit.objects.get(id=habit_id, user_id=usuario)
            expected_progress = habit.repetitions
            
            habit_creation_date = habit.created_at.date()
            current_date = datetime.now().date()
            
            date_list = []
            progress_list = []
            
            current = habit_creation_date
            while current <= current_date:
                date_list.append(current)
                
                # Obtener el progreso del historial
                daily_progress = habit.progress_history.filter(
                    date=current
                ).values_list('progress', flat=True).first() or 0
                
                progress_list.append(daily_progress)
                current += timedelta(days=1)
            
            progress_labels = [date.strftime("%Y-%m-%d") for date in date_list]
            progress_data = progress_list
            total_specificHabit = habit.repetitions
            best_progress = max(progress_list) if progress_list else 0
            
        except Habit.DoesNotExist:
            context['error'] = "Hábito no encontrado."

    # Progreso acumulado de todos los hábitos a lo largo del tiempo
    habits_progress_over_time = (
        habits
        .values('created_at__date')
        .annotate(total_progress=Sum('current_progress'))
        .order_by('created_at__date')
    )

    # Extraer etiquetas y datos de progreso acumulado
    labels_allHabitsProgress = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in habits_progress_over_time]
    all_habits_data = [entry['total_progress'] for entry in habits_progress_over_time]

    # Agregar datos duplicados si solo hay un punto de progreso acumulado
    if len(labels_allHabitsProgress) == 1:
        labels_allHabitsProgress.append(labels_allHabitsProgress[0])
        all_habits_data.append(all_habits_data[0])

    # Datos de progreso de todos los hábitos por fecha
    all_habits_progress_by_date = (
        habits
        .values("created_at__date")
        .annotate(
            total_progress=Sum("current_progress"),
            total_repetitions=Sum("repetitions")
        )
        .order_by("created_at__date")
    )
    
    # Extraer etiquetas y datos para el progreso total y actual de todos los hábitos
    labels_allHabitsProgress = [entry["created_at__date"].strftime("%Y-%m-%d") for entry in all_habits_progress_by_date]
    data_total_allHabitsProgress = [entry["total_repetitions"] for entry in all_habits_progress_by_date]
    data_current_allHabitsProgress = [entry["total_progress"] for entry in all_habits_progress_by_date]

    # Calcular porcentaje de finalización de hábitos
    completion_labels = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in all_habits_progress_by_date]
    completion_percentage_data = [
        (entry['total_progress'] / entry['total_repetitions']) * 100 if entry['total_repetitions'] > 0 else 0
        for entry in all_habits_progress_by_date
    ]

    # Agregar duplicados si hay un solo punto de progreso
    if len(completion_labels) == 1:
        completion_labels.append(completion_labels[0])
        completion_percentage_data.append(completion_percentage_data[0])

    # Datos para gráfico de frecuencia de uso
    frequency_counter = dict(Counter(freq_names))
    labels_mostUsedFrequencies = list(frequency_counter.keys())
    data_mostUsedFrequencies = list(frequency_counter.values())

    # Datos para gráfico de repeticiones por hábito
    names_repetitionsPerHabit = habits.values_list('name', flat=True)
    repetitions_repetitionsPerHabit = habits.values_list('repetitions', flat=True)
    
    # Verificar si no hay datos en byCategory y byFrequency
    no_data = not allCategories and not allFrequencies
    
    # Actualizar el contexto con datos procesados y serializados en JSON
    context.update({
        "categories": categories,
        "total_habits_created": total_habits_created,
        "best_progress": best_progress,
        "progress_labels": json.dumps(progress_labels),
        "progress_data": json.dumps(progress_data),
        "user_habits": Habit.objects.filter(user_id=usuario),
        "expected_progress": expected_progress, 
        "completion_labels": json.dumps(completion_labels),
        "completion_percentage_data": json.dumps(completion_percentage_data),
        "frequency_counter": json.dumps(frequency_counter),
        "no_data": no_data,
        
        # Gráfico de Categorías más Creadas
        "byCategory": json.dumps(allCategories),
        "byFrequency": json.dumps(allFrequencies),

        # Gráfico de Repeticiones por Hábito
        "names_repetitionsPerHabit": json.dumps(list(names_repetitionsPerHabit)),
        "repetitions_repetitionsPerHabit": json.dumps(list(repetitions_repetitionsPerHabit)),
        
        # Gráfico de Frecuencias más usadas
        "labels_mostUsedFrequencies": json.dumps(labels_mostUsedFrequencies),
        "data_mostUsedFrequencies": json.dumps(data_mostUsedFrequencies),
        
        # Gráfico de Hábitos Creados
        "labels_createdHabits": json.dumps(labels_createdHabits), 
        "data_createdHabits": json.dumps(data_createdHabits),

        # Gráfico de Hábito Específico  
        "labels_specificHabit": json.dumps(progress_labels),
        "total_specificHabit": total_specificHabit,
        "habit_data_total_specificHabit": json.dumps(progress_data), 
    })

    return render(request, "stats/index.html", context)