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
from django.http import JsonResponse


@login_required
def estadisticas(request):

    usuario        = request.user
    start_date     = request.GET.get('start_date')
    end_date       = request.GET.get('end_date')
    category_id    = request.GET.get('category')
    frequency      = request.GET.get('frequency')
    categories     = Category.objects.all()
    habits         = Habit.objects.all()
    category_names = []
    freq_names     = []

    if not (category_id is None):
        habits = habits.filter(user_id=usuario, category_id=category_id)
    
    if not (frequency is None):
        habits = habits.filter(user_id=usuario, frequency=frequency)

    if (frequency is None) and (frequency is None):
        habits = habits.filter(user_id=usuario)

    if start_date and end_date:
        habits = habits.filter(created_at__range=[parse_date(start_date), parse_date(end_date)])
 
    for h in habits:
        category_names.append(h.category.name)
    
    for f in habits:
        freq_names.append(f.frequency)

    allCategories  = dict(Counter(category_names)) # [{"category": count}]
    allFrequencies = dict(Counter(freq_names))

    return render(request, 'stats/index.html', {
         'byCategory': json.dumps(allCategories),
         'byFrequency': json.dumps(allFrequencies),
         'categories': categories
        })
