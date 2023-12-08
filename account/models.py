from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings
from django.utils.timezone import now


class User(AbstractUser):
    image = models.ImageField(upload_to='image_user', null=True, blank=True)
    is_verified_email = models.BooleanField(default=False)


class EmailVerification(models.Model):
    code = models.UUIDField(verbose_name='код для подтверждения', unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')
    created = models.DateTimeField(verbose_name='дата создания', auto_now_add=True)
    expiration = models.DateTimeField(verbose_name='время истечения')

    class Meta:
        verbose_name = 'Активированная почта'
        verbose_name_plural = 'Активированные почты'

    def __str__(self):
        return f'Подтверждённая почта для {self.user.email}'

    def send_verification_email(self):
        link = reverse('account:emailverification', kwargs={'email': self.user.email, 'code': self.code})
        verification_link = f'{settings.DOMAIN_NAME}{link}'
        subject = f'Подтверждение учётной записи {self.user.username}'
        message = 'Для подтверждения учётной записи для {} перейдите по ссылке: {}'.format(
            self.user.email,
            verification_link
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def is_expired(self):
        return True if now() >= self.expiration else False
