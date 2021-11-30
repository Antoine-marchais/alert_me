from django.http import HttpResponse, HttpRequest
from django.views import View


class Alerts(View):

    def get(self, request: HttpRequest, user_id):
        return HttpResponse(f"Hello, user {user_id} You're at the alerts index")

    def post(self, request: HttpRequest, user_id):
        return HttpResponse(f"Hello, user {user_id}, You're adding an alert")


class Alert(View):

    def get(self, request: HttpRequest, user_id, alert_id):
        return HttpResponse(f"Hello, user {user_id}, You requested alert {alert_id}")
