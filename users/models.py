from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.db.models import F


class UserQuerySet(models.QuerySet):

    def add_to_balance(self, amount):
        return self.update(balance=F('balance') + amount)


class UserManager(BaseUserManager.from_queryset(UserQuerySet)):
    pass


class User(AbstractUser):
    inn = models.CharField(verbose_name='ИНН', max_length=13, null=True)
    balance = models.DecimalField(verbose_name='Баланс', max_digits=10, decimal_places=2, null=True)
    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователь'

    def __str__(self):
        return self.get_full_name() or self.username

    def _write_off(self, amount):
        self.balance = F('balance') - amount
        self.save(update_fields=['balance'])

    def write_off(self, amount):
        self._write_off(amount)
        self.refresh_from_db()
