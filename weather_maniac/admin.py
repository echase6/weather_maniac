"""flutter Admin Configuration."""

from django.contrib import admin

from . import models

admin.site.register(models.DayRecord)
admin.site.register(models.ActualDayRecord)
admin.site.register(models.ErrorHistogram)
admin.site.register(models.ErrorBin)
