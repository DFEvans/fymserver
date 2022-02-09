from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect

from .models import Map


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world!")


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
