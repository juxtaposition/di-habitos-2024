from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Habit
from .forms import HabitForm

def habit_list(request):
    if request.user.is_authenticated:
        print(request.user.id)
        habits = Habit.objects.filter(user=request.user)
        userQuery = User.objects.get(pk=request.user.id)
        return render(request, 'home.html', {'habits': habits, 'username': userQuery.first_name})
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
    return render(request, 'habit/confirm_delete.html', {'habit': habit}) # TODO: Use our delete view
