from django.http import HttpRequest, JsonResponse
from django.views import View
from django.apps import apps
from google.cloud.scheduler import CloudSchedulerClient
import json
from datetime import datetime
import pandas as pd

from hf_alerts.utils import fetch_availabilities, set_scheduled_job, get_availabilities_difference
from hf_alerts.notifiers import notify_by_mail, notify_by_tl


class Alerts(View):

    def get(self, request: HttpRequest, user_id):
        user_ref = apps.get_app_config("hf_alerts").db.collection("users").document(user_id)
        resp = dict(user_id=user_ref.id, **user_ref.get().to_dict())
        resp["alerts"] = [dict(alert_id=alert_ref.id, **alert_ref.to_dict()) for alert_ref in user_ref.collection("hf_alerts").stream()]
        return JsonResponse(resp)

    def post(self, request: HttpRequest, user_id):
        user_ref = apps.get_app_config("hf_alerts").db.collection("users").document(user_id)
        alert_params = json.loads(request.body)
        alert_ref = user_ref.collection("hf_alerts").document()
        job_name = set_scheduled_job(user_id, alert_ref.id)
        alert_ref.set({"name": job_name, "params": alert_params})
        resp = {}
        resp["alert_id"] = alert_ref.id
        resp["params"] = alert_params
        resp["job_name"] = job_name
        return JsonResponse(resp)

class AlertView(View):

    def get(self, request: HttpRequest, user_id, alert_id):
        user_ref = apps.get_app_config("hf_alerts").db.collection("users").document(user_id)
        alert_params = user_ref.collection("hf_alerts").document(alert_id).get().to_dict()["params"]
        availabilities = fetch_availabilities(
            reservation_date=datetime.fromisoformat(alert_params["start_time"]).date(),
            length=float(alert_params["min_span"]),
            min_size=float(alert_params["min_size"]),
            start_time=alert_params["start_time"],
            end_time=alert_params["end_time"]
        )
        resp = {"availabilities": []}
        for idx, row in availabilities.iterrows():
            resp["availabilities"].append(row.to_dict())
        return JsonResponse(resp)

    @staticmethod
    def delete(request: HttpRequest, user_id, alert_id):
        client = CloudSchedulerClient()
        user_ref = apps.get_app_config("hf_alerts").db.collection("users").document(user_id)
        alert_ref = user_ref.collection("hf_alerts").document(alert_id)
        for availability in alert_ref.collection("availabilities").stream():
            availability.reference.delete()
        client.delete_job(name=alert_ref.get().to_dict()["name"])
        alert_ref.delete()
        return JsonResponse({"deleted_id": alert_id})


def get_new_availabilities(request: HttpRequest, user_id, alert_id):
    user_ref = apps.get_app_config("hf_alerts").db.collection("users").document(user_id)
    alert_ref = user_ref.collection("hf_alerts").document(alert_id)
    alert_params = alert_ref.get().to_dict()["params"]
    if datetime.fromisoformat(alert_params["start_time"]) < datetime.now():
        return AlertView.delete(request, user_id, alert_id)
    current_availabilities = fetch_availabilities(
        reservation_date=datetime.fromisoformat(alert_params["start_time"]).date(),
        length=float(alert_params["min_span"]),
        min_size=float(alert_params["min_size"]),
        start_time=alert_params["start_time"],
        end_time=alert_params["end_time"]
    )
    saved_availabilities = pd.DataFrame(
        [{"id": availability.id, **availability.to_dict()} for availability in alert_ref.collection("availabilities").stream()],
        columns=["date", "name", "size", "start_time", "end_time", "span", "id"])
    to_add, to_remove = get_availabilities_difference(current_availabilities, saved_availabilities)
    resp = {"availabilities": []}
    for idx, row in to_add.iterrows():
        resp["availabilities"].append(row.to_dict())
        alert_ref.collection("availabilities").document().set(row.to_dict())
    for idx, row in to_remove.iterrows():
        alert_ref.collection("availabilities").document(row["id"]).delete()
    if len(to_add) > 0:
        notify_by_mail(to_add)
        notify_by_tl(to_add)
    return JsonResponse(resp)






