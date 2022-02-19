from datetime import datetime
from typing import cast

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

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


@csrf_exempt
def update_modified_date(request: HttpRequest, pk: int) -> HttpResponse:
    if "modified_date" not in request.POST:
        return HttpResponseBadRequest("modified_date parameter missing")

    try:
        modified_date = datetime.strptime(
            request.POST["modified_date"], r"%Y-%m-%d"
        ).date()
    except ValueError:
        return HttpResponseBadRequest("Malformed modified_date, must be YYYY-MM-DD")

    if Map.objects.filter(pk=pk).exists():
        map_obj = cast(Map, Map.objects.get(pk=pk))
        map_obj.modified_date = modified_date
    else:
        map_obj = cast(
            Map,
            Map.objects.create(
                id=pk,
                modified_date=modified_date,
            ),
        )

    map_obj.save()

    return HttpResponse()


def update_file(request: HttpRequest, pk: int, file_attr: str, file_ext: str):
    if file_attr not in request.FILES:
        return HttpResponseBadRequest(f"{file_attr} not provided")

    file_obj = request.FILES[file_attr]

    if Map.objects.filter(pk=pk).exists():
        map_obj = cast(Map, Map.objects.get(pk=pk))
    else:
        map_obj = cast(
            Map,
            Map.objects.create(
                id=pk,
                modified_date=timezone.now(),
            ),
        )

    getattr(map_obj, file_attr).save(f"{pk}.{file_ext}", file_obj)

    map_obj.save()

    return HttpResponse()


@csrf_exempt
def update_jpg_file(request: HttpRequest, pk: int) -> HttpResponse:
    return update_file(request, pk, "jpg_file", "jpg")


@csrf_exempt
def update_yrd_file(request: HttpRequest, pk: int) -> HttpResponse:
    return update_file(request, pk, "yrd_file", "yrd")


@csrf_exempt
def update_his_file(request: HttpRequest, pk: int) -> HttpResponse:
    return update_file(request, pk, "his_file", "his")
