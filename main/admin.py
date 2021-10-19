'''
admin interface
'''
from django.contrib import admin

from main.forms import ParametersForm

from main.models import Parameters
from main.models import ParameterSet
from main.models import ParameterSetType
from main.models import ParameterSetTypePlayer

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
admin.site.register(ParameterSetTypePlayer)
