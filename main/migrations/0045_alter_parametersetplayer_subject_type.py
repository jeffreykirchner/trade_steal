# Generated by Django 3.2.8 on 2021-12-03 19:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_auto_20211203_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametersetplayer',
            name='subject_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_players_d', to='main.parametersettype'),
        ),
    ]
