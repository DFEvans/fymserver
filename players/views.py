from typing import cast

from django.conf import settings
from django.core import mail
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django_otp.oath import totp

from .models import Player

AUTH_CODE_EMAIL_TEXT = """Hello!

Someone (probably you) has requested an authentication code for your Freight Yard Manager account.

If this was not you, please ignore this message.

The authentication code is:

{auth_code}

Enter this code into the prompt in FYM to complete the authentication procedure."""


def generate_otp(key: str, step: int, timestamp: int, drift: int = 0) -> int:
    return totp(key.encode(), step=step, t0=timestamp, drift=drift)


@csrf_exempt
def send_auth_code(request: HttpRequest) -> HttpResponse:
    player: str = request.POST.get("player", "")
    if not player:
        return HttpResponseBadRequest("No player specified")

    if Player.objects.filter(username=player).exists():
        player_obj = cast(Player, Player.objects.get(username=player))
        if player_obj.email:

            otp = generate_otp(
                settings.SECRET_KEY + player_obj.token,
                settings.OTP_STEP_SECS,
                int(timezone.now().timestamp()),
            )

            message = AUTH_CODE_EMAIL_TEXT.format(auth_code=otp)

            mail.send_mail(
                "[Freight Yard Manager] Authentication Code",
                message,
                "noreply@fymanager.com",
                [player_obj.email],
            )

    return HttpResponse()


def validate_otp(
    key: str, step: int, timestamp: int, drift_range: int, input_otp: int
) -> bool:
    for i in range(-drift_range, drift_range + 1):
        if input_otp == generate_otp(key, step, timestamp, drift=i):
            return True

    return False


@csrf_exempt
def check_auth_code(request: HttpRequest) -> HttpResponse:
    player: str = request.POST.get("player", "")
    if not player:
        return HttpResponseBadRequest("No player specified")

    otp_raw = request.POST.get("otp", "")
    if not otp_raw:
        return HttpResponseBadRequest("No OTP specified")

    if not Player.objects.filter(username=player).exists():
        return HttpResponseForbidden()

    player_obj = cast(Player, Player.objects.get(username=player))

    try:
        otp = int(otp_raw)
    except TypeError:
        return HttpResponseBadRequest("Unparseable OTP")

    if not validate_otp(
        settings.SECRET_KEY + player_obj.token,
        settings.OTP_STEP_SECS,
        int(timezone.now().timestamp()),
        settings.OTP_DRIFT_RANGE,
        otp,
    ):
        return HttpResponseForbidden()

    return JsonResponse({"token": player_obj.token})
