from datetime import datetime
from typing import cast

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect

from .models import Map


# Create your views here.
def index(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"maps": [map_obj.id for map_obj in Map.objects.all()]})


def _get_map_file(pk: int, file_attr: str) -> HttpResponse:
    map_obj = get_object_or_404(Map, pk=pk)
    return redirect(getattr(map_obj, file_attr).url)


def jpg_file(request: HttpRequest, pk: int) -> HttpResponse:
    return _get_map_file(pk, "jpg_file")


def yrd_file(request: HttpRequest, pk: int) -> HttpResponse:
    return _get_map_file(pk, "yrd_file")


def his_file(request: HttpRequest, pk: int) -> HttpResponse:
    return _get_map_file(pk, "his_file")


def modified_date(request: HttpRequest, pk: int) -> JsonResponse:
    map_obj = get_object_or_404(Map, pk=pk)
    return JsonResponse({"modified_date": map_obj.modified_date})


def update(request: HttpRequest, pk: int) -> HttpResponse:
    if "modified_date" not in request.POST:
        return HttpResponseBadRequest("modified_date parameter missing")

    try:
        modified_date = datetime.strptime(
            request.POST["modified_date"], r"%Y-%m-%d"
        ).date()
    except ValueError:
        return HttpResponseBadRequest("Malformed modified_date, must be YYYY-MM-DD")

    jpg_exists = "jpg_file" in request.FILES
    yrd_exists = "yrd_file" in request.FILES
    his_exists = "his_file" in request.FILES

    if Map.objects.filter(pk=pk).exists():
        map_obj = cast(Map, Map.objects.get(pk=pk))
        map_obj.modified_date = modified_date
    else:
        if not (jpg_exists and yrd_exists and his_exists):
            return HttpResponseBadRequest(
                f"Map {pk} does not exist, all files must be provided"
            )

        map_obj = cast(
            Map,
            Map.objects.create(
                id=pk,
                modified_date=modified_date,
            ),
        )

    if jpg_exists:
        map_obj.jpg_file.save(f"{pk}.jpg", request.FILES["jpg_file"])

    if yrd_exists:
        map_obj.yrd_file.save(f"{pk}.yrd", request.FILES["yrd_file"])

    if his_exists:
        map_obj.his_file.save(f"{pk}.his", request.FILES["his_file"])

    map_obj.save()

    return HttpResponse()
