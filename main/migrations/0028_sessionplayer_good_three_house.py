# Generated by Django 3.2.9 on 2021-11-14 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_rename_good_count_parameterset_number_of_goods'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayer',
            name='good_three_house',
            field=models.IntegerField(default=0, verbose_name='Good three in house'),
        ),
    ]