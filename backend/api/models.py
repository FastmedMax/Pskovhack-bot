from django.db import models


# Create your models here.
class Case(models.Model):
    title = models.CharField(verbose_name="Название", max_length=60)
    description = models.TextField(verbose_name="Описание")


class Event(models.Model):
    title = models.CharField(verbose_name="Название", max_length=60)
    description = models.TextField(verbose_name="Описание")


class Callback(models.Model):
    class Type(models.TextChoices):
        TELEGRAM = "TELEGRAM", "Телеграм"
        VK = "VK", "ВК"

    name = models.CharField(verbose_name="Имя", max_length=30)
    user_id = models.CharField(verbose_name="ID", max_length=50)
    contact = models.CharField(verbose_name="Контакт", max_length=60)
    text = models.CharField(verbose_name="Название", max_length=60)
    type = models.CharField(
        verbose_name="Тип",
        choices=Type.choices,
        max_length=30)
