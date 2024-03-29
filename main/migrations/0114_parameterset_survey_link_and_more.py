# Generated by Django 4.0.7 on 2022-11-29 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0113_parametersettype_autarky_earnings'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterset',
            name='survey_link',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Survey Link'),
        ),
        migrations.AddField(
            model_name='parameterset',
            name='survey_required',
            field=models.BooleanField(default=False, verbose_name='Survey Required'),
        ),
    ]
