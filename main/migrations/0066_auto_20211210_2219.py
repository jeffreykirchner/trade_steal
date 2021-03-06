# Generated by Django 3.2.8 on 2021-12-10 22:19

from django.db import migrations
from main.models import Avatar
from main.models import ParameterSetPlayer

def do_python(apps, schema_editor):
    avatar = Avatar.objects.first()

    if not avatar:
        avatar = Avatar()
        avatar.save()
    
    ParameterSetPlayer.objects.all().update(avatar=avatar)
    
class Migration(migrations.Migration):

    dependencies = [
        ('main', '0065_alter_parametersetplayer_avatar'),
    ]

    operations = [
        migrations.RunPython(do_python)
    ]
