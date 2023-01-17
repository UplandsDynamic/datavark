from django.contrib import admin
from .models import Report, Loc, Color, Time, Date, Type

# Register your models here.


@admin.register(Report, Loc, Color, Time, Date, Type)
class ReportAdmin(admin.ModelAdmin):
    pass


class LocAdmin(admin.ModelAdmin):
    pass


class ColorAdmin(admin.ModelAdmin):
    pass


class TimeAdmin(admin.ModelAdmin):
    pass


class DateAdmin(admin.ModelAdmin):
    pass


class TypeAdmin(admin.ModelAdmin):
    pass
