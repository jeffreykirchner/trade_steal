# Generated by Django 3.2.9 on 2021-12-09 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0059_parameterset_test_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parameterset',
            name='test_mode',
            field=models.BooleanField(default=False, verbose_name='Test Mode'),
        ),
    ]