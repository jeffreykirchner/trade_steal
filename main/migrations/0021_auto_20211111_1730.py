# Generated by Django 3.2.9 on 2021-11-11 17:30

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20211110_1806'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parametersetgood',
            options={'ordering': ['id'], 'verbose_name': 'Parameter Set Good', 'verbose_name_plural': 'Parameter Set Goods'},
        ),
        migrations.AddField(
            model_name='parametersetplayer',
            name='good_one',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_players_a', to='main.parametersetgood'),
        ),
        migrations.AddField(
            model_name='parametersetplayer',
            name='good_three',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_player_c', to='main.parametersetgood'),
        ),
        migrations.AddField(
            model_name='parametersetplayer',
            name='good_two',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_players_b', to='main.parametersetgood'),
        ),
        migrations.AddConstraint(
            model_name='parametersetplayer',
            constraint=models.CheckConstraint(check=models.Q(('good_one', django.db.models.expressions.F('good_two')), _negated=True), name='good_one_unique'),
        ),
        migrations.AddConstraint(
            model_name='parametersetplayer',
            constraint=models.CheckConstraint(check=models.Q(('good_one', django.db.models.expressions.F('good_three')), _negated=True), name='good_two_unique'),
        ),
        migrations.AddConstraint(
            model_name='parametersetplayer',
            constraint=models.CheckConstraint(check=models.Q(('good_two', django.db.models.expressions.F('good_three')), _negated=True), name='good_thee_unique'),
        ),
    ]