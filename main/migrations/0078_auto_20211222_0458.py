# Generated by Django 3.2.9 on 2021-12-22 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0077_parametersetavatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterset',
            name='avatar_grid_col_count',
            field=models.IntegerField(default=3, verbose_name='Avatar Grid Col Count'),
        ),
        migrations.AddField(
            model_name='parameterset',
            name='avatar_grid_row_count',
            field=models.IntegerField(default=3, verbose_name='Avatar Grid Row Count'),
        ),
    ]