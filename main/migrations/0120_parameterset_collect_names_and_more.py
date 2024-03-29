# Generated by Django 4.1.5 on 2023-03-06 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0119_remove_sessionplayer_production_total_equals_100'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterset',
            name='collect_names',
            field=models.BooleanField(default=True, verbose_name='Collect Names'),
        ),
        migrations.AddField(
            model_name='parameterset',
            name='post_forward_link',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='After Study Forwarding Link'),
        ),
    ]
