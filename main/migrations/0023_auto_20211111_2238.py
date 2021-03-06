# Generated by Django 3.2.8 on 2021-11-11 22:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20211111_2234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametersetplayer',
            name='good_one',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_players_a', to='main.parametersetgood'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='parametersetplayer',
            name='good_three',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_player_c', to='main.parametersetgood'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='parametersetplayer',
            name='good_two',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_players_b', to='main.parametersetgood'),
            preserve_default=False,
        ),
    ]
