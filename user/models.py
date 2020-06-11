from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    phone = models.CharField(max_length=11, unique=True, blank=False, verbose_name='手机号码')
    photo = models.ImageField(upload_to='upload/%Y%m%d/', blank=True, verbose_name='头像')
    desc = models.CharField(max_length=256, blank=True,verbose_name='简介')

    def __str__(self):
        return self.phone

    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name




