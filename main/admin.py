'''
admin interface
'''
from django.contrib import admin

from main.forms import ParametersForm
from main.forms import SessionFormAdmin
from main.forms import InstructionFormAdmin

from main.models import Parameters
from main.models import ParameterSet
from main.models import ParameterSetType
from main.models import ParameterSetPlayer
from main.models import ParameterSetPlayerGroup

from main.models import Session
from main.models import SessionPlayer
from main.models import SessionPlayerChat
from main.models import SessionPlayerMove
from main.models import SessionPlayerPeriod

from main.models.avatar import Avatar
from main.models.instruction import Instruction

class ParametersAdmin(admin.ModelAdmin):
    '''
    parameters model admin
    '''
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    form = ParametersForm

    actions = []

admin.site.register(Parameters, ParametersAdmin)

admin.site.register(ParameterSet)
admin.site.register(ParameterSetType)
admin.site.register(ParameterSetPlayer)

class ParameterSetPlayerGroupAdmin(admin.ModelAdmin):

    list_display = ['parameter_set_player', 'group_number', 'period']
    ordering=['parameter_set_player', 'period']

admin.site.register(ParameterSetPlayerGroup, ParameterSetPlayerGroupAdmin)


class SessionAdmin(admin.ModelAdmin):
    form = SessionFormAdmin

admin.site.register(Session, SessionAdmin)


admin.site.register(SessionPlayer)
admin.site.register(SessionPlayerChat)
admin.site.register(SessionPlayerMove)
admin.site.register(SessionPlayerPeriod)

admin.site.register(Avatar)

class InstructionAdmin(admin.ModelAdmin):
    form = InstructionFormAdmin

admin.site.register(Instruction, InstructionAdmin)