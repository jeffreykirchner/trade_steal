# Generated by Django 3.2.11 on 2022-01-11 16:30

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0095_alter_parameterset_instruction_set'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpDocs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=300, verbose_name='Title')),
                ('text', tinymce.models.HTMLField(default='', max_length=100000, verbose_name='Help Doc Text')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Help Doc',
                'verbose_name_plural': 'Help Docs',
                'ordering': ['title'],
            },
        ),
        migrations.AddConstraint(
            model_name='helpdocs',
            constraint=models.UniqueConstraint(fields=('title',), name='unique_help_doc'),
        ),
    ]