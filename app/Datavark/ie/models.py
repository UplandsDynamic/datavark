from django.db import models
from django.contrib.gis.db.models import PointField


class Loc(models.Model):
    """
    Class to define the model to hold report locations relations
    """

    place_name = models.CharField(
        max_length=200,
        verbose_name="Observation place name(s)",
        help_text="Name(s) of the location(s) of observation",
    )
    coordinates = PointField(
        verbose_name="Observation coordinates",
        help_text="Coordinates of the location(s) of observation (longitude, latitude)",
    )

    def __str__(self):
        return f"{self.place_name} ({self.coordinates.x}, {self.coordinates.y})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["place_name", "coordinates"],
                name="Unique for place_name, coordinates pairs",
            )
        ]


class Date(models.Model):
    """
    Class to define the model to hold report dates relations
    """

    date = models.DateField(
        unique=True,
        verbose_name="Observation date(s)",
        help_text="Date(s) associated with the observation.",
    )

    def __str__(self):
        return self.date.strftime("%d-%m-%Y")


class Time(models.Model):
    """
    Class to define the model to hold report times relations
    """

    time = models.TimeField(
        unique=True,
        verbose_name="Observation time(s)",
        help_text="Time(s) associated with the observation.",
    )

    def __str__(self):
        return self.time.strftime("%H:%M")


class Color(models.Model):
    """
    Class to define the model to hold report colours relations
    """

    color = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Observation colour(s)",
        help_text="Colour(s) associated with the observation.",
    )

    def __str__(self):
        return self.color


class Type(models.Model):
    """
    Class to define the model to hold report observation type relations
    """

    type = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Observation type(s)",
        help_text="Observation types, e.g., 'lights', 'saucer', 'triangle'.",
    )

    def __str__(self):
        return self.type


class Report(models.Model):
    """
    Class to define the model to hold observation reports
    """

    record_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Record created",
        help_text="Date record was created in this database.",
    )
    last_mod = models.DateTimeField(
        auto_now=True,
        verbose_name="Last modified",
        help_text="Date record was last modified in this database.",
    )
    record_junked = models.BooleanField(
        default=False,
        verbose_name="Record junked",
        help_text="Record marked for deletion",
    )
    source_name = models.CharField(
        max_length=200,
        verbose_name="Source name",
        help_text="Name of the original data source",
    )
    source_url = models.URLField(
        verbose_name="Source URL",
        help_text="Web link to the original record (as of time of entry).",
        unique=True,
    )
    obs_txt = models.TextField(
        verbose_name="Report text", help_text="Unmodified text of the original report."
    )
    obs_types = models.ManyToManyField(
        Type,
        verbose_name="Observation type(s)",
        help_text="Observation types, e.g., 'lights', 'saucer', 'triangle'.",
    )
    obs_colors = models.ManyToManyField(
        Color,
        verbose_name="Observation colour(s)",
        help_text="Colour(s) associated with the observation.",
    )
    obs_locs = models.ManyToManyField(
        Loc,
        verbose_name="Observation location(s)",
        help_text="Name(s) of the location(s) of observation, i.e., place name, (longitude, latitude)",
    )
    obs_dates = models.ManyToManyField(
        Date,
        verbose_name="Observation date(s)",
        help_text="Date(s) associated with the observation.",
    )

    obs_times = models.ManyToManyField(
        Time,
        verbose_name="Observation time(s)",
        help_text="Time(s) associated with the observation.",
    )

    def __str__(self):
        return self.record_created.strftime("%d-%m-%Y")
