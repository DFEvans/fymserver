import os
from datetime import datetime

from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from players.decorators import valid_player_required
from players.models import Player

from .models import Train, TrainState


# Create your views here.
@valid_player_required
def index(request: HttpRequest) -> HttpResponse:
    search_player: str = request.POST.get("search_player", "")
    filename: str = request.POST.get("filename", "")
    upload_before: str = request.POST.get("upload_before", "")

    trains = Train.objects.filter(state=TrainState.AVAILABLE)
    if search_player:
        trains = trains.filter(
            Q(from_player=search_player) | Q(to_player=search_player)
        )
    if filename:
        trains = trains.filter(train_file__contains=filename)
    if upload_before:
        try:
            upload_before_date = datetime.strptime(upload_before, r"%Y-%m-%d").date()
        except ValueError:
            return HttpResponseBadRequest("Malformed upload_before, must be YYYY-MM-DD")
        trains = trains.filter(upload_date__lte=upload_before_date)

    return JsonResponse(
        [{"pk": train.pk, "file": train.train_file.name} for train in trains.all()],
        safe=False,
    )


@csrf_exempt
@valid_player_required
def download(request: HttpRequest, pk: int) -> HttpResponse:
    player: str = request.POST.get("player", "")
    if not player:
        return HttpResponseBadRequest("No player specified")

    player_obj: Player = get_object_or_404(Player, username=player)
    train: Train = get_object_or_404(Train, pk=pk)

    if train.state != TrainState.AVAILABLE:
        return HttpResponseBadRequest("Train unavailable")

    train.set_downloaded(player_obj)
    train.save()

    return redirect(train.train_file.url)


@csrf_exempt
@valid_player_required
def upload(request: HttpRequest) -> HttpResponse:
    if len(request.FILES) != 1:
        return HttpResponseBadRequest(
            f"Expected 1 file attachment, got {len(request.FILES)}"
        )

    filename: str = request.POST.get("filename", "")
    if not filename:
        return HttpResponseBadRequest("No filename provided")

    file_obj = request.FILES[list(request.FILES.keys())[0]]
    tokens = os.path.splitext(filename)[0].split("-")
    to_player = tokens[3]
    from_player = tokens[4]

    train_obj = Train(
        to_player=to_player,
        from_player=from_player,
    )
    train_obj.train_file.save(filename, file_obj)
    train_obj.save()

    return HttpResponse()
