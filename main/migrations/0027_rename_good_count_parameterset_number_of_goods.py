# Generated by Django 3.2.9 on 2021-11-13 00:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_parameterset_number_of_goods'),
    ]

    operations = [
        migrations.RenameField(
            model_name='parameterset',
            old_name='number_of_goods',
            new_name='good_count',
        ),
    ]
