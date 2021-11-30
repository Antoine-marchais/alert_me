from django.urls import path

from . import views

urlpatterns = [
    path(f"webhook/", views.index, name='index'),
    path('notify_user/<int:user_id>', views.notify_user)
]