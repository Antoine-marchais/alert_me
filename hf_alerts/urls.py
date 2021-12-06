from django.urls import path

from .views import AlertView, Alerts, get_new_availabilities

urlpatterns = [
    path('', Alerts.as_view(), name='index'),
    path('<str:alert_id>/', AlertView.as_view()),
    path('<str:alert_id>/new_availabilities/', get_new_availabilities)
]