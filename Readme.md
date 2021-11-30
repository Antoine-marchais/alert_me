# Reservation Alerts

This project allows the creation of telegram alerts based on the availability of rehersal rooms. The structure can be
extended to add new source of alerts and new notification handlers.

## Services

We use a micro-service architecture, where each alert source and each notification canal is a new microservice.

### HF Scraper

The HF Scraper checks for availabilities of rehersal rooms and calls the telegram micro-service when a new availability
is detected.

**Endpoints:**
- `GET user/<user_id>/hf_alerts/`: Get all created alerts by user
- `POST user/<user_id>/hf_alerts/`: Create a new alert for the user
- `GET user/<user_id>/hf_alerts/<alert_id>`: checks for new availabilities on the created alert

### Telegram Handler

The Telegram Handler receives message from the telegram API, and calls the hf scraper service accordingly. It also
notify the user when new availabilities are detected

**Endpoints:**
- `POST tl_handler/webhook`: Send updates to the webhook
- `POST tl_handler/notify_user/<user_id>`: Notify the user of the new availabilities 