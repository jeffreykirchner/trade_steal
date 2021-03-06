# Generated by Django 3.2.8 on 2021-12-13 22:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0068_auto_20211213_1728'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionPlayerNotice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(default='', max_length=1000, verbose_name='Notice Text')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('session_period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_player_notices_a', to='main.sessionperiod')),
                ('session_player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_player_notices_b', to='main.sessionplayer')),
            ],
            options={
                'verbose_name': 'Session Player Notice',
                'verbose_name_plural': 'Session Player Notice',
                'ordering': ['timestamp'],
            },
        ),
        migrations.AddConstraint(
            model_name='sessionplayernotice',
            constraint=models.CheckConstraint(check=models.Q(('text', ''), _negated=True), name='notice_text_not_empty'),
        ),
    ]
