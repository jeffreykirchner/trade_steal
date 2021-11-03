# Generated by Django 3.2.8 on 2021-10-24 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_remove_parametersetplayer_period_groups'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='parametersetplayergroup',
            constraint=models.UniqueConstraint(fields=('parameter_set_player', 'period'), name='unique_player_period_group'),
        ),
    ]