# Generated by Django 3.2.9 on 2021-12-22 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0078_auto_20211222_0458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametersetavatar',
            name='avatar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_avatars_b', to='main.avatar'),
        ),
        migrations.AddConstraint(
            model_name='parametersetavatar',
            constraint=models.UniqueConstraint(fields=('parameter_set', 'grid_location_row', 'grid_location_col'), name='unique_parameter_set_avatar'),
        ),
    ]