# Generated by Django 4.1.3 on 2022-11-29 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0115_parametersetplayer_survey_complete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parametersetplayer',
            name='survey_complete',
        ),
        migrations.AddField(
            model_name='sessionplayer',
            name='survey_complete',
            field=models.BooleanField(default=False, verbose_name='Survey Complete'),
        ),
    ]
