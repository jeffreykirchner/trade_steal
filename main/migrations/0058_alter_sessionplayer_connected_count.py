# Generated by Django 3.2.8 on 2021-12-08 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0057_auto_20211208_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionplayer',
            name='connected_count',
            field=models.IntegerField(default=0, verbose_name='Number of consumer connections'),
        ),
    ]
