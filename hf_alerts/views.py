from django.http import HttpRequest, JsonResponse
from django.views import View
from django.apps import apps
import json
from datetime import datetime
import pandas as pd

from hf_alerts.utils import fetch_availabilities


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
        alert_ref.set(alert_params)
        resp = {}
        resp["alert_id"] = alert_ref.id
        resp["params"] = alert_params
        return JsonResponse(resp)


class AlertView(View):

    def get(self, request: HttpRequest, user_id, alert_id):
        user_ref = apps.get_app_config("hf_alerts").db.collection("users").document(user_id)
        alert_dict = user_ref.collection("hf_alerts").document(alert_id).get().to_dict()
        availabilities = fetch_availabilities(
            reservation_date=datetime.fromisoformat(alert_dict["start_time"]).date(),
            length=float(alert_dict["min_span"]),
            min_size=float(alert_dict["min_size"]),
            start_time=alert_dict["start_time"],
            end_time=alert_dict["end_time"]
        )
        resp = {"availabilities": []}
        for idx, row in availabilities.iterrows():
            resp["availabilities"].append(row.to_dict())
        return JsonResponse(resp)

    def delete(self, request: HttpRequest, user_id, alert_id):
        user_ref = apps.get_app_config("hf_alerts").db.collection("users").document(user_id)
        user_ref.collection("hf_alerts").document(alert_id).delete()
        return JsonResponse({"deleted_id": alert_id})


def get_new_availabilities(request: HttpRequest, user_id, alert_id):
    user_ref = apps.get_app_config("hf_alerts").db.collection("users").document(user_id)
    alert_ref = user_ref.collection("hf_alerts").document(alert_id)
    alert_dict = alert_ref.get().to_dict()
    current_availabilities = fetch_availabilities(
        reservation_date=datetime.fromisoformat(alert_dict["start_time"]).date(),
        length=float(alert_dict["min_span"]),
        min_size=float(alert_dict["min_size"]),
        start_time=alert_dict["start_time"],
        end_time=alert_dict["end_time"]
    )
    saved_availabilities = pd.DataFrame(
        [{"id": availability.id, **availability.to_dict()} for availability in alert_ref.collection("availabilities").stream()],
        columns=["date", "name", "size", "start_time", "end_time", "span", "id"])
    current_availabilities["primary_key"] = \
        current_availabilities["name"] + current_availabilities["start_time"] + current_availabilities["span"].map(str)
    saved_availabilities["primary_key"] = \
        saved_availabilities["name"] + saved_availabilities["start_time"] + saved_availabilities["span"].map(str)
    to_add = current_availabilities[~current_availabilities["primary_key"]
        .isin(saved_availabilities["primary_key"])].drop(columns=["primary_key"])
    to_remove = saved_availabilities.loc[~saved_availabilities["primary_key"]
        .isin(current_availabilities["primary_key"]), ["id"]]
    resp = {"availabilities": []}
    for idx, row in to_add.iterrows():
        resp["availabilities"].append(row.to_dict())
        alert_ref.collection("availabilities").document().set(row.to_dict())
    for idx, row in to_remove.iterrows():
        alert_ref.collection("availabilities").document(row["id"]).delete()
    return JsonResponse(resp)






