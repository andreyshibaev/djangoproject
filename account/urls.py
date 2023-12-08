from django.contrib.auth.views import LogoutView
from django.urls import path
from django.contrib.auth.decorators import login_required
from account import views

app_name = 'account'

urlpatterns = [
    path('login/', views.LoginUserView.as_view(), name='loginform'),
    path('register/', views.RegisterUserView.as_view(), name='registerform'),
    path('profile/', login_required(views.ProfileUpdateView.as_view()), name='profileform'),
    path('profile/<int:user_id>/delete', views.del_profile_image, name='delphotouser'),
    path('logout/',  LogoutView.as_view(), name='logoutform'),
    path('verify/<str:email>/<uuid:code>/', views.EmailVerificationView.as_view(), name='emailverification'),
    path('changepassword/', views.ChangePasswordView.as_view(), name='changepassword'),
]
