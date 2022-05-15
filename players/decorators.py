from typing import cast

from django.core.exceptions import BadRequest, PermissionDenied
from django.http import HttpRequest

from .models import Player


def valid_player_required(func):
    def wrapper(request: HttpRequest, *args, **kwargs):
        player: str = request.POST.get("player", "")
        token: str = request.POST.get("token", "")

        if not player:
            raise BadRequest("No player specified")

        if not token:
            raise BadRequest("No token specified")

        if not Player.objects.filter(username=player).exists():
            raise PermissionDenied()

        player_obj = cast(Player, Player.objects.get(username=player))

        if not player_obj.validate_token(token):
            raise PermissionDenied()

        return func(request, *args, **kwargs)

    return wrapper
