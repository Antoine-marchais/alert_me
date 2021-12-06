from datetime import datetime
import requests
import pandas as pd
import os
import yagmail

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


def notify_by_mail(availabilities):
    date = availabilities["date"].iloc[0]
    str_availabilities = "\n".join([
        f"- {row['name']} ({row['size']} m²): on the {row['date']}, from {row['start_time']} to {row['start_time']}"
        for idx, row in availabilities.iterrows()])
    message = f"""the following new availabilities have been detected:
        
{str_availabilities}
        
Proceed to the following address to make a reservation:
https://www.quickstudio.com/en/studios/hf-music-studio-14/bookings
"""
    receiver = os.environ["GMAIL_RECEIVER"]
    yag = yagmail.SMTP(
        user=os.environ["GMAIL_ACCOUNT"],
        password=os.environ["GMAIL_PASSWORD"]
    )
    yag.send(
        to=os.environ["GMAIL_RECEIVER"],
        subject=f"[HF SCRAPPER] New room available for the {date}",
        contents=message
    )
