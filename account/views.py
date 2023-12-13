from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect, get_object_or_404
from account.forms import UserLoginForm, UserRegisterForm, ProfileForm
from django.urls import reverse_lazy
from account.forms import UserPasswordChangeForm
from django.contrib.messages.views import SuccessMessageMixin
from account.services.mixins import UserIsNotAuthenticated
from common.views import TitleMixin
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView
from account.models import User
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.models import Site
from django.core.mail import send_mail


class LoginUserView(UserIsNotAuthenticated, TitleMixin, LoginView):
    template_name = 'account/login.html'
    form_class = UserLoginForm
    title = 'Войти в кабинет'

    def get_success_url(self):
        messages.success(self.request, 'Вы успешно вошли в аккаунт!')
        return reverse_lazy('homeapp:homeapp')


class RegisterUserView(UserIsNotAuthenticated, TitleMixin, SuccessMessageMixin, CreateView):
    model = get_user_model()
    template_name = 'account/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('account:loginform')
    success_message = 'Успешная регистрация!'
    title = 'Регистрация пользователя'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_url = reverse_lazy('account:confirm_email', kwargs={'uidb64': uid, 'token': token})
        current_site = Site.objects.get_current().domain
        send_mail(
            'Подтвердите свой электронный адрес',
            f'Пожалуйста, перейдите по следующей ссылке,'
            f' чтобы подтвердить свой адрес электронной почты: http://{current_site}{activation_url}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return redirect('account:email_confirmation_sent')


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
    success_url = reverse_lazy('account:profileform')
    title = 'Изменить пароль'


class UserConfirmEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            messages.info(request, 'Поздравляю! Вы активированы!')
            return redirect('account:email_confirmed')
        else:
            return redirect('account:email_confirmation_failed')


class EmailConfirmationSentView(TemplateView):
    template_name = 'account/email_confirmation_sent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Письмо активации отправлено'
        return context


class EmailConfirmedView(TemplateView):
    template_name = 'account/email_confirmed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ваш электронный адрес активирован'
        return context


class EmailConfirmationFailedView(TemplateView):
    template_name = 'account/email_confirmation_failed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ваш электронный адрес не активирован'
        return context
