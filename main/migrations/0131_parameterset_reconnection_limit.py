# Generated by Django 4.2.16 on 2024-09-27 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0130_session_id_string'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterset',
            name='reconnection_limit',
            field=models.IntegerField(default=25, verbose_name='Limit Subject Screen Reconnection Trys'),
        ),
    ]
