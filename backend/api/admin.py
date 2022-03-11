from django.contrib import admin

from .models import Callback, Case, Event


# Register your models here.
admin.site.register(Callback)
admin.site.register(Case)
admin.site.register(Event)
