from django.db import models


# Create your models here.
class Case(models.Model):
    title = models.CharField(verbose_name="Название", max_length=60)
    description = models.TextField(verbose_name="Описание")


class Event(models.Model):
    title = models.CharField(verbose_name="Название", max_length=60)
    description = models.TextField(verbose_name="Описание")
