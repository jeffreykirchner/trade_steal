# Generated by Django 3.2.8 on 2021-12-07 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_auto_20211206_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayer',
            name='connected',
            field=models.BooleanField(default=False),
        ),
    ]
