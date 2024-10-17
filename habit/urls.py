from django.urls import path
from .views import habit_list, add_habit, delete_habit

urlpatterns = [
    path('', habit_list, name='habit_list'),
    path('habit/add/', add_habit, name='add_habit'),
    path('habit/delete/<int:habit_id>/', delete_habit, name='delete_habit'),
]