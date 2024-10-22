from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from habit.models import Habit, Category
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count, Q
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

    # Inicializar queryset de hábitos y listas para los nombres de categorías y frecuencias
    habits = Habit.objects.filter(user_id=usuario)
    category_names = []
    freq_names = []

    # Filtrar los hábitos por categoría, frecuencia, y rango de fechas si se especifica
    if category_id:
        habits = habits.filter(category_id=category_id)
    if frequency:
        habits = habits.filter(frequency=frequency)
    if start_date and end_date:
        habits = habits.filter(
            created_at__range=[parse_date(start_date), parse_date(end_date)]
        )

    # Obtener los nombres de las categorías y frecuencias
    for h in habits:
        category_names.append(h.category.name)
        freq_names.append(h.frequency)

    # Contar hábitos por categoría y frecuencia
    allCategories = dict(Counter(category_names))
    allFrequencies = dict(Counter(freq_names))

    # Obtener el conteo total de hábitos creados
    total_habits_created = habits.count()

    # Obtener datos para la gráfica de hábitos creados por fecha
    habits_by_date = (
        habits.values("created_at__date")
        .annotate(count=Count("id"))
        .order_by("created_at__date")
    )
    # Obtener datos para la gráfica de hábitos creados por fecha
    habits_by_date = (
        habits.values("created_at__date")
        .annotate(count=Count("id"))
        .order_by("created_at__date")
    )

    # Definir variables separadas para labels y data
    labels = [
        habit["created_at__date"].strftime("%Y-%m-%d") for habit in habits_by_date
    ]
    data = [habit["count"] for habit in habits_by_date]

    # Luego puedes crear steps_data como un diccionario si lo necesitas
    steps_data = {"labels": labels, "data": data}

    # Agregar datos simulados para otras gráficas (pasos, agua, promedio diario)
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
        "labels": labels,  # Nueva variable para etiquetas
        "data": data,  # Nueva variable para datos
        "water_data": json.dumps(water_data),
        "daily_average_data": json.dumps(daily_average_data),
        "grafico1_data": json.dumps(grafico1_data),
        "grafico2_data": json.dumps(grafico2_data),
        "grafico3_data": json.dumps(grafico3_data),
        "grafico4_data": json.dumps(grafico4_data),
    }

    return render(request, "stats/index.html", context)
