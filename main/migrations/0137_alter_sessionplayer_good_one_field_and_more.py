# Generated by Django 4.2.16 on 2024-11-07 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0136_sessionplayer_good_one_field_production_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionplayer',
            name='good_one_field',
            field=models.IntegerField(default=0, verbose_name='Good one in field'),
        ),
        migrations.AlterField(
            model_name='sessionplayer',
            name='good_two_field',
            field=models.IntegerField(default=0, verbose_name='Good two in field'),
        ),
    ]
