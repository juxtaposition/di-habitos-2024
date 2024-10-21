from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from .models import Habit
from .forms import HabitForm

@login_required
def habit_list(request):
    habits = Habit.objects.filter(user=request.user)
    for habit in habits:
        habit.reset_progress_if_needed()
    userQuery = User.objects.get(pk=request.user.id)
    return render(request, 'home.html', {'habits': habits, 'username': userQuery.first_name})



@login_required
def add_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.category_id = form.data.get('category')
            habit.save()
            return JsonResponse({'success': True})
    else:
        form = HabitForm()
    
    html = render_to_string('habit/habit_form_modal.html', {'form': form}, request=request)
    return JsonResponse({'html': html})


@login_required
def edit_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
    else:
        form = HabitForm(instance=habit)
    
    html = render_to_string('habit/habit_form_modal.html', {'form': form}, request=request)
    return JsonResponse({'html': html})


@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        habit.delete()
        return redirect('habit_list')
    return render(request, 'habit/confirm_delete.html', {'habit': habit}) # TODO: Use our delete view


@login_required
@require_POST
def increment_progress(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    habit.increment_progress()
    return JsonResponse({
        'current_progress': habit.current_progress,
        'progress_percentage': habit.get_progress_percentage(),
        'repetitions': habit.repetitions
    })