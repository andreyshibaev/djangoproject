from django.urls import path
from homeapp.views import homepage

app_name = 'homeapp'

urlpatterns = [
    path('', homepage, name='homeapp'),
]
