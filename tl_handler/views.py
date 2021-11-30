from django.http import HttpResponse, HttpRequest


def index(request: HttpRequest):
    return HttpResponse("Hello from webhook, You're at the tl_handler index")


def notify_user(request: HttpRequest, user_id):
    return HttpResponse(f"Hello from tl_handler, You're trying to notify user {user_id}")

