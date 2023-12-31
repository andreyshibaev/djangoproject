from django.contrib.auth.views import (LogoutView, PasswordResetView, PasswordResetDoneView,
                                       PasswordResetConfirmView, PasswordResetCompleteView)
from django.urls import path, reverse_lazy
from django.contrib.auth.decorators import login_required
from account import views

app_name = 'account'

urlpatterns = [
    path('login/', views.LoginUserView.as_view(), name='loginform'),
    path('register/', views.RegisterUserView.as_view(), name='registerform'),
    path('profile/', login_required(views.ProfileUpdateView.as_view()), name='profileform'),
    path('profile/<int:user_id>/delete', views.del_profile_image, name='delphotouser'),
    path('logout/', LogoutView.as_view(), name='logoutform'),
    path('changepassword/', views.UserPasswordChange.as_view(), name='changepassword'),
    path('password-reset/', PasswordResetView.as_view(
        template_name='account/password_reset_form.html',
        email_template_name='account/password_reset_email.html',
        success_url=reverse_lazy('account:password_reset_done')
    ), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(
        template_name='account/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='account/password_reset_confirm.html',
             success_url=reverse_lazy('account:password_reset_complete')),
         name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(
        template_name='account/password_reset_complete.html'),
         name='password_reset_complete'),

    path('email-confirmation-sent/', views.EmailConfirmationSentView.as_view(), name='email_confirmation_sent'),
    path('confirm-email/<str:uidb64>/<str:token>/', views.UserConfirmEmailView.as_view(), name='confirm_email'),
    path('email-confirmed/', views.EmailConfirmedView.as_view(), name='email_confirmed'),
    path('confirm-email-failed/', views.EmailConfirmationFailedView.as_view(), name='email_confirmation_failed'),

]
