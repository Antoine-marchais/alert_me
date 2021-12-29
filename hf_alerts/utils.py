from datetime import datetime
import requests
import pandas as pd
import os
from google.cloud import scheduler

from alert_me.models import Availability


def fetch_availabilities(reservation_date, length=2, min_size=0, name=None, start_time=None, end_time=None, **kw):
    r = requests.get(
        url="https://www.quickstudio.com/en/studios/hf-music-studio-14/bookings",
        headers={"accept": "application/json"},
        params={"date": reservation_date.isoformat()})
    results = r.json()
    availabilities = []
    for room in results:
        room_availabilities = get_availabilities(room["bookings"], room["open"], room["close"])
        for availabily in room_availabilities:
            availabilities.append({
                "date": reservation_date.isoformat(),
                "name": room["name"],
                "size": room["size"],
                "start_time": availabily.start.strftime("%H:%M"),
                "end_time": availabily.end.strftime("%H:%M"),
                "span": availabily.span
            })
    availabilities = pd.DataFrame(availabilities, columns=["date", "name", "size", "start_time", "end_time", "span"])
    return filter_availabilities(availabilities, length, min_size, name, start_time, end_time)


def get_availabilities(bookings, open, close):
    last_end_date = open
    availabilities = []
    for booking in bookings:
        if booking["band"] is None:
            continue
        availabilities.append(Availability(datetime.fromisoformat(last_end_date), datetime.fromisoformat(booking["start"])))
        last_end_date = booking["end"]
    availabilities.append(Availability(datetime.fromisoformat(last_end_date), datetime.fromisoformat(close)))
    return list(filter(lambda avail: avail.span > 0, availabilities))


def filter_availabilities(avail, length=2, min_size=0, name=None, start_time=None, end_time=None):
    avail = avail[avail["span"] >= length]
    avail = avail[avail["size"] >= min_size]
    if name: avail = avail[avail["name"] == name]
    if start_time: avail = avail[avail["start_time"] >= start_time]
    if end_time: avail = avail[avail["end_time"] <= end_time]
    return avail


def get_availabilities_difference(current_availabilities, saved_availabilities):
    current_availabilities["primary_key"] = \
        current_availabilities["name"] + current_availabilities["start_time"] + current_availabilities["span"].map(str)
    saved_availabilities["primary_key"] = \
        saved_availabilities["name"] + saved_availabilities["start_time"] + saved_availabilities["span"].map(str)
    to_add = current_availabilities[~current_availabilities["primary_key"]
        .isin(saved_availabilities["primary_key"])].drop(columns=["primary_key"])
    to_remove = saved_availabilities.loc[~saved_availabilities["primary_key"]
        .isin(current_availabilities["primary_key"]), ["id"]]
    return to_add, to_remove


def set_scheduled_job(user_id, alert_id):
    minute = datetime.now().minute
    client = scheduler.CloudSchedulerClient()
    parent = f"projects/{os.environ['GCP_PROJECT']}/locations/{os.environ['GCP_APP_LOCATION']}"
    job = client.create_job(
        request={
            "parent": parent,
            "job": {
                "schedule": f"{minute} * * * *",
                "time_zone": "Europe/Paris",
                "app_engine_http_target": {
                    "http_method": 2,
                    "app_engine_routing": {"service": "default"},
                    "relative_uri": f"/user/{user_id}/hf_alerts/{alert_id}/new_availabilities/"
                }
            }
        },
    )
    return job.name


