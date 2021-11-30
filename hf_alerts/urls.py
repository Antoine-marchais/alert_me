from django.urls import path

from .views import Alert, Alerts

urlpatterns = [
    path('', Alerts.as_view(), name='index'),
    path('<int:alert_id>/', Alert.as_view())
]