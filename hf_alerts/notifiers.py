import os
import yagmail
import requests


def notify_by_mail(availabilities):
    date = availabilities["date"].iloc[0]
    str_availabilities = "\n".join([
        f"- {row['name']} ({row['size']} m²): on the {row['date']}, from {row['start_time']} to {row['end_time']}"
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


def notify_by_tl(availabilities):
    date = availabilities["date"].iloc[0]
    response_body = {
        "date": date,
        "availabilities": [{
            "name": row["name"],
            "size": row["size"],
            "start_time": row["start_time"],
            "end_time": row["end_time"]
        } for idx, row in availabilities.iterrows()],
        "url": f"https://www.quickstudio.com/en/studios/hf-music-studio-14/bookings?date={date}",
        "to": int(os.environ["TL_RECEIVER"])
    }
    requests.post(url=os.environ["TL_HANDLER_URL"]+"/external/new_availabilities", json=response_body)


