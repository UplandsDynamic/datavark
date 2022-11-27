from django.db import models
from django.contrib.gis.db.models import PointField


class Loc(models.Model):
    place_name = models.CharField(max_length=200)
    coordinates = PointField()


class Date(models.Model):
    date = models.DateField()


class Time(models.Model):
    time = models.TimeField()


class Color(models.Model):
    color = models.CharField(max_length=200)


class Type(models.Model):
    type = models.CharField(max_length=200)


class Report(models.Model):
    record_created = models.DateTimeField(auto_now_add=True)
    last_mod = models.DateTimeField(auto_now=True)
    source_name = models.CharField(max_length=200)
    source_url = models.URLField()
    obs_txt = models.TextField()
    obs_types = models.ManyToManyField(Type)
    obs_colors = models.ManyToManyField(Color)
    obs_locs = models.ManyToManyField(Loc)
    obs_dates = models.ManyToManyField(Date)
    obs_times = models.ManyToManyField(Time)
