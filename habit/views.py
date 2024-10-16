from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import HabitForm
from .models import Habit

def habit_list(request):
    if request.user.is_authenticated:
        habits = Habit.objects.filter(user=request.user)
        return render(request, 'home.html', {'habits': habits})
    else:
        return redirect('login')

@login_required
def add_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            return redirect('habit_list')
    else:
        form = HabitForm()
    return render(request, 'habit/add.html', {'form': form}) # TODO: use our create view

@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        habit.delete()
        return redirect('habit_list')
    return render(request, 'habit/add.html', {'form': form}) # TODO: use our create view

# @login_required
def dashboard_view(request):
    steps_data = [1000, 9500, 8000, 12000, 6000]
    water_data = [2, 2.5, 2.2, 2, 2.4, 2.3, 2]
    avg_data = {
        '2h': [120, 140, 160, 180, 200, 220, 240],
        '30m': [30, 40, 50, 60, 70, 80, 90],
        '5h': [300, 350, 400, 450, 500, 550, 600]
    }
    return render(request, 'dashboard.html', {
        'steps_data': steps_data,
        'water_data': water_data,
        'avg_data': avg_data
    })
