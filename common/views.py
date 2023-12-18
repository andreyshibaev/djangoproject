from django.http import HttpResponseServerError
from django.shortcuts import render


def page_not_found(request, exception=None):
    return render(request, '404.html', status=404)


def forbidden(request, exception=None):
    return render(request, '403.html', status=403)


def server_error(request):
    return HttpResponseServerError('<h1>Ошибка сервера!</h1>', status=500)
