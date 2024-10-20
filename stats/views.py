from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from habit.models import Habit, Category
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count, Q
import json
from datetime import datetime
from collections import Counter

@login_required
def estadisticas(request):

    usuario = request.user

    fecha_inicio   = request.GET.get('fecha_inicio')
    fecha_fin      = request.GET.get('fecha_fin')
    category_id    = request.GET.get('categoria')
    categories     = Category.objects.all()
    category_names = []

    if not (category_id is None):
        habits = Habit.objects.all().filter(user_id=usuario, category_id=category_id)
    else:
        habits = Habit.objects.all().filter(user_id=usuario)

    if fecha_inicio and fecha_fin:
        habits = habits.filter(created_at__range=[parse_date(fecha_inicio), parse_date(fecha_fin)])

    # this is better way to get the all categories by count
    for h in habits:
        category_names.append(h.category.name)
    
    allCategories = dict(Counter(category_names))


    print(allCategories)
    # if categorias:
    #     compras = compras.filter(fruta__categorias__id__in=categorias).distinct()

    # frutas_compradas = compras.values('fruta__nombre').annotate(total_compradas=Sum('cantidad')).order_by('-total_compradas')

    # total_compras = compras.aggregate(total=Sum('cantidad'))['total'] or 0
    # if total_compras > 0:
    #     for fruta in frutas_compradas:
    #         fruta['porcentaje'] = (fruta['total_compradas'] / total_compras) * 100
    # else:
    #     for fruta in frutas_compradas:
    #         fruta['porcentaje'] = 0
    
    # todas_categorias = Categoria.objects.all()

    # contexto = {
    #     'frutas_compradas': json.dumps(list(frutas_compradas)),
    #     'todas_categorias': todas_categorias,
    # }
    return render(request, 'stats/index.html', { 
        'habits': json.dumps(allCategories),
         "categories": categories
        })
