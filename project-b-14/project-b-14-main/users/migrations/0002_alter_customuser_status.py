# Generated by Django 4.2.4 on 2023-11-28 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="status",
            field=models.CharField(
                choices=[("regular", "regular"), ("admin", "admin")],
                default="regular",
                max_length=255,
            ),
        ),
    ]
