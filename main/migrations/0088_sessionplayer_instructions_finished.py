# Generated by Django 3.2.9 on 2022-01-03 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0087_auto_20220103_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayer',
            name='instructions_finished',
            field=models.BooleanField(default=False, verbose_name='Instructions Finished'),
        ),
    ]