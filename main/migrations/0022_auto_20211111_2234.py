# Generated by Django 3.2.8 on 2021-11-11 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20211111_1730'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='parametersetgood',
            name='unique_good_label',
        ),
        migrations.RemoveConstraint(
            model_name='parametersetgood',
            name='unique_good_color',
        ),
        migrations.AddConstraint(
            model_name='parametersetgood',
            constraint=models.UniqueConstraint(fields=('parameter_set', 'label'), name='unique_parameter_set_good_label'),
        ),
        migrations.AddConstraint(
            model_name='parametersetgood',
            constraint=models.UniqueConstraint(fields=('parameter_set', 'rgb_color'), name='unique_parameter_set_good_rgb'),
        ),
    ]
