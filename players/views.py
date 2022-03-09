from typing import cast

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse

from .models import Player


# Create your views here.
def uuid(request: HttpRequest) -> HttpResponse:
    username: str = request.GET.get("username", "")
    if not username:
        return HttpResponseBadRequest("No username specified")

    if Player.objects.filter(username=username).exists():
        player_obj = cast(Player, Player.objects.get(username=username))
    else:
        player_obj = Player(username=username)
        player_obj.save()

    return JsonResponse({"uuid": player_obj.id})
