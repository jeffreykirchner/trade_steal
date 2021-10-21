# Generated by Django 3.2.8 on 2021-10-21 21:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_alter_parametersettype_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParameterSetPlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_type', models.CharField(choices=[('One', 'One'), ('Two', 'Two')], default='One', max_length=100)),
                ('id_label', models.CharField(default='1', max_length=2, verbose_name='ID Label')),
                ('location', models.IntegerField(default=1, verbose_name='Location number (1-8)')),
                ('period_groups', models.JSONField(default=dict, verbose_name='Group by period')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parameter_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_players', to='main.parameterset')),
            ],
            options={
                'verbose_name': 'Parameter Set Type Player',
                'verbose_name_plural': 'Parameter Set Type Players',
                'ordering': ['id_label'],
            },
        ),
        migrations.DeleteModel(
            name='ParameterSetTypePlayer',
        ),
    ]
