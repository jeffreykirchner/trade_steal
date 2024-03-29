# Generated by Django 4.1.5 on 2023-03-06 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0121_remove_parameterset_collect_names_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterset',
            name='prolific_session_id',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Prolific session ID'),
        ),
        migrations.AddField(
            model_name='parameterset',
            name='prolific_study_id',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Prolific Study ID'),
        ),
    ]
