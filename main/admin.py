'''
admin interface
'''
from django.utils.translation import ngettext

from django.contrib import admin
from django.contrib import messages
from django.conf import settings

from main.forms import ParametersForm
from main.forms import SessionFormAdmin
from main.forms import InstructionFormAdmin
from main.forms import InstructionSetFormAdmin

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

from main.models import Avatar
from main.models import  HelpDocs

from main.models.instruction_set import InstructionSet
from main.models.instruction import Instruction

admin.site.site_header = settings.ADMIN_SITE_HEADER

@admin.register(Parameters)
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

class ParameterSetPlayerInline(admin.TabularInline):

      extra = 0  
      model = ParameterSetPlayer
      can_delete = True   

class ParameterSetTypeInline(admin.TabularInline):

      extra = 0  
      model = ParameterSetType
      can_delete = False   

@admin.register(ParameterSet)
class ParameterSetAdmin(admin.ModelAdmin):
    inlines = [
        ParameterSetTypeInline, ParameterSetPlayerInline,
      ]

    list_display = ['period_count', 'period_length_production', 'period_length_trade', 'break_period_frequency', 'allow_stealing', 'group_chat', 'private_chat', 'town_count', 'good_count']

admin.site.register(ParameterSetType)
admin.site.register(ParameterSetPlayer)

@admin.register(ParameterSetPlayerGroup)
class ParameterSetPlayerGroupAdmin(admin.ModelAdmin):

    list_display = ['parameter_set_player', 'group_number', 'period']
    ordering=['parameter_set_player', 'period']    

@admin.register(SessionPlayer)
class SessionPlayerAdmin(admin.ModelAdmin):
    
    readonly_fields = ['session', 'parameter_set_player']
    

class SessionPlayerInline(admin.TabularInline):

    def has_add_permission(self, request, obj=None):
        return False
    
    @admin.display(description='Player ID')
    def get_parameter_set_player_id_label(self, obj):
        return obj.parameter_set_player.id_label

    extra = 0  
    model = SessionPlayer
    can_delete = False   
    show_change_link = True
    fields = ['name', 'email', 'student_id', 'survey_complete']
    readonly_fields = ('get_parameter_set_player_id_label',)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    form = SessionFormAdmin

    def refresh(self, request, queryset):

        for i in queryset.all():
            i.parameter_set.json(update_required=True)

        self.message_user(request, ngettext(
                '%d session is refreshed.',
                '%d sessions are refreshed.',
                queryset.count(),
        ) % queryset.count(), messages.SUCCESS)
    
    def reset(self, request, queryset):

        for i in queryset.all():
            i.reset_experiment()
            
        self.message_user(request, ngettext(
                '%d session is reset.',
                '%d sessions are reset.',
                queryset.count(),
        ) % queryset.count(), messages.SUCCESS)

    readonly_fields = ['parameter_set', 'channel_key', 'controlling_channel']
    inlines = [SessionPlayerInline]
    actions = ['reset', 'refresh']

admin.site.register(SessionPlayerChat)
admin.site.register(SessionPlayerMove)
admin.site.register(SessionPlayerPeriod)

admin.site.register(Avatar)

#instruction set page
class InstructionPageInline(admin.TabularInline):
      '''
      instruction page admin screen inline
      '''
      extra = 0  
      form = InstructionFormAdmin
      model = Instruction
      can_delete = True

@admin.register(InstructionSet)
class InstructionSetAdmin(admin.ModelAdmin):
    form = InstructionSetFormAdmin

    def duplicate_set(self, request, queryset):
            '''
            duplicate instruction set
            '''
            if queryset.count() != 1:
                  self.message_user(request,"Select only one instruction set to copy.", messages.ERROR)
                  return

            base_instruction_set = queryset.first()

            instruction_set = InstructionSet()
            instruction_set.save()
            instruction_set.copy_pages(base_instruction_set.instructions)

            self.message_user(request,f'{base_instruction_set} has been duplicated', messages.SUCCESS)

    duplicate_set.short_description = "Duplicate Instruction Set"

    inlines = [
        InstructionPageInline,
      ]
    
    actions = [duplicate_set]

admin.site.register(HelpDocs)