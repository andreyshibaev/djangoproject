from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect, get_object_or_404
from account.forms import UserLoginForm, UserRegisterForm, ProfileForm
from django.urls import reverse_lazy
from account.forms import UserPasswordChangeForm
from django.contrib.messages.views import SuccessMessageMixin

from account.services.auth_redirect import UserIsNotAuthenticated
from account.services.mixins import DataMixin
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


class LoginUserView(DataMixin, UserIsNotAuthenticated, LoginView):
    template_name = 'account/login.html'
    form_class = UserLoginForm
    title_page = 'Войти в аккаунт'

    def form_invalid(self, form):
        messages.error(self.request, 'Неверное имя или пароль', extra_tags='danger')
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        messages.success(self.request, 'Вы успешно вошли в аккаунт!', extra_tags='success')
        return reverse_lazy('homeapp:homeapp')


class RegisterUserView(DataMixin, UserIsNotAuthenticated, SuccessMessageMixin, CreateView):
    model = get_user_model()
    template_name = 'account/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('account:loginform')
    success_message = 'Успешная регистрация!'
    title_page = 'Регистрация пользователя'

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


class ProfileUpdateView(DataMixin, UpdateView):
    model = get_user_model()
    template_name = 'account/profile.html'
    form_class = ProfileForm
    title_page = 'Личный кабинет'

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
        messages.success(request, 'Фото пользователя удалено!', extra_tags='info')
    return redirect('account:profileform')


class UserPasswordChange(DataMixin, SuccessMessageMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'account/changepassword.html'
    success_message = 'Успешно изменили пароль'
    success_url = reverse_lazy('account:profileform')
    title_page = 'Форма для изменения пароля'


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


class EmailConfirmationSentView(DataMixin, TemplateView):
    template_name = 'account/email_confirmation_sent.html'
    title_page = 'Письмо активации отправлено'


class EmailConfirmedView(DataMixin, TemplateView):
    template_name = 'account/email_confirmed.html'
    title_page = 'Ваш электронный адрес активирован'


class EmailConfirmationFailedView(DataMixin, TemplateView):
    template_name = 'account/email_confirmation_failed.html'
    title_page = 'Ошибка активации почты'
