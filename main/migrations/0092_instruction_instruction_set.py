# Generated by Django 3.2.9 on 2022-01-04 17:40

from django.db import migrations, models
import django.db.models.deletion

import main

def do_python(apps, schema_editor):
    global parameter_set

    parameter_set = main.models.InstructionSet.objects.first()

    if not parameter_set:
        parameter_set = main.models.InstructionSet()
        parameter_set.save()
    
    main.models.Instruction.objects.all().update(instruction_set=parameter_set)

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0091_auto_20220104_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructionset',
            name='action_page_chat',
            field=models.IntegerField(default=4, verbose_name='Required Action: Chat'),
        ),
        migrations.AddField(
            model_name='instructionset',
            name='action_page_production',
            field=models.IntegerField(default=2, verbose_name='Required Action: Production'),
        ),
        migrations.AddField(
            model_name='instructionset',
            name='action_page_move',
            field=models.IntegerField(default=3, verbose_name='Required Action: Move'),
        ),
        migrations.AddField(
            model_name='instruction',
            name='instruction_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='instructions', to='main.instructionset'),
        ),
        migrations.RunPython(do_python),
    ]
