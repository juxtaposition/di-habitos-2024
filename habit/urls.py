from django.urls import path
from .views import edit_habit, habit_list, add_habit, delete_habit
from . import views


urlpatterns = [
    path('', habit_list, name='habit_list'),
    path('habit/add/', add_habit, name='add_habit'),
    path('habit/edit/<int:habit_id>/', edit_habit, name='edit_habit'),
    path('habit/delete/<int:habit_id>/', delete_habit, name='delete_habit'),
    path('habit/increment-progress/<int:habit_id>/', views.increment_progress, name='increment_progress'),
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/check-new/', views.check_new_notifications, name='check_new_notifications'),
]