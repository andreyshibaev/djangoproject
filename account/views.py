from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponseRedirect, redirect, get_object_or_404
from account.forms import UserLoginForm, UserRegisterForm, ProfileForm
from django.urls import reverse, reverse_lazy
from account.forms import UserPasswordChangeForm
from django.contrib.messages.views import SuccessMessageMixin
from common.views import TitleMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from account.models import User, EmailVerification
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib import messages


class LoginUserView(TitleMixin, SuccessMessageMixin, LoginView):
    template_name = 'account/login.html'
    form_class = UserLoginForm
    success_message = 'Вы успешно вошли!'
    title = 'Войти в кабинет'

    def get_success_url(self):
        return reverse_lazy('homeapp:homeapp')


class RegisterUserView(TitleMixin, SuccessMessageMixin, CreateView):
    model = get_user_model()
    template_name = 'account/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('account:loginform')
    success_message = 'Успешная регистрация!'
    title = 'Регистрация пользователя'


class ProfileUpdateView(TitleMixin, UpdateView):
    model = get_user_model()
    template_name = 'account/profile.html'
    form_class = ProfileForm
    title = 'Личный кабинет'

    def get_success_url(self):
        return reverse_lazy('account:profileform')

    def get_object(self, queryset=None):
        return self.request.user


@login_required
def del_profile_image(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id, username=request.user)
    profile_image = profile_user.image
    if request.method == 'POST':
        profile_image.delete()
        messages.success(request, 'Фото пользователя удалено!')
    return redirect('homeapp:homeapp')


class UserPasswordChange(TitleMixin, SuccessMessageMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'account/changepassword.html'
    success_message = 'Успешно изменили пароль'
    success_url = reverse_lazy('homeapp:homeapp')
    title = 'Изменить пароль'


class EmailVerificationView(TitleMixin, TemplateView):
    title = 'Страница подтверждения почты'
    template_name = 'account/email_verification.html'

    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = User.objects.get(email=kwargs['email'])
        emailverifications = EmailVerification.objects.filter(user=user, code=code)
        if emailverifications.exists() and not emailverifications.first().is_expired():
            user.is_verified_email = True
            user.save()
            return super(EmailVerificationView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('homeapp:homeapp'))
