# Generated by Django 3.2.9 on 2022-01-04 02:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0089_auto_20220104_0206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instruction',
            name='text',
        ),
    ]
