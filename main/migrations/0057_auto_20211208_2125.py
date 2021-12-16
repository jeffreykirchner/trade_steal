# Generated by Django 3.2.8 on 2021-12-08 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0056_rename_connected_sessionplayer_connecting'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayer',
            name='connected_count',
            field=models.IntegerField(default=50, verbose_name='Number of consumer connections'),
        ),
        migrations.AlterField(
            model_name='sessionplayer',
            name='connecting',
            field=models.BooleanField(default=False, verbose_name='Consumer is connecting'),
        ),
    ]