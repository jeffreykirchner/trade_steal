# Generated by Django 4.2.16 on 2024-11-19 16:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0137_alter_sessionplayer_good_one_field_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayermove',
            name='session_player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_player_moves_d', to='main.sessionplayer'),
        ),
    ]