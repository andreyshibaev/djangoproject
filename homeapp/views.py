from django.shortcuts import render

def homepage(request):
    context = {
        'title': 'Главная страница'
    }
    return render(request, 'homeapp/home.html', context)