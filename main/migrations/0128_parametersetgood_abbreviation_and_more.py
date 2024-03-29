# Generated by Django 4.2.11 on 2024-03-06 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0127_parameterset_information_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametersetgood',
            name='abbreviation',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='Good Abbreviation'),
        ),
        migrations.AlterField(
            model_name='parametersetgood',
            name='label',
            field=models.CharField(default='Orange', max_length=10, verbose_name='Good Label'),
        ),
        migrations.AlterField(
            model_name='parametersetgood',
            name='rgb_color',
            field=models.CharField(default='#FF5733', max_length=10, verbose_name='Good RGB Color'),
        ),
        migrations.AddConstraint(
            model_name='parametersetgood',
            constraint=models.UniqueConstraint(fields=('parameter_set', 'abbreviation'), name='unique_parameter_set_good_abbreviation'),
        ),
    ]
