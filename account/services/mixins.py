from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class DataMixin:
    title_page = None
    extra_context = {}

    def __init__(self):
        if self.title_page:
            self.extra_context['title'] = self.title_page

class UserIsNotAuthenticated(UserPassesTestMixin):

    def __init__(self):
        self.request = None

    def test_func(self):
        if self.request.user.is_authenticated:
            messages.info(self.request, 'Вы уже авторизованы. Вы не можете посетить эту страницу!')
            raise PermissionDenied
        return True

    def handle_no_permission(self):
        return redirect('homeapp:homeapp')


