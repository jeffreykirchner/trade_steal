# Generated by Django 3.2.8 on 2021-12-10 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0062_rename_avatars_avatar'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='avatar',
            options={'ordering': ['label'], 'verbose_name': 'Avatar', 'verbose_name_plural': 'Avatars'},
        ),
        migrations.AddField(
            model_name='parameterset',
            name='show_avatars',
            field=models.BooleanField(default=False, verbose_name='Show Avatars'),
        ),
    ]