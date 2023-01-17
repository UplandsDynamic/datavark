# Generated by Django 4.1.3 on 2022-12-03 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ie", "0002_alter_loc_coordinates_alter_loc_place_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="source_url",
            field=models.URLField(
                help_text="Web link to the original record (as of time of entry).",
                unique=True,
                verbose_name="Source URL",
            ),
        ),
    ]
