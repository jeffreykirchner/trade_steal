'''
parameterset player group edit form
'''

from django import forms

from main.models import ParameterSetPlayerGroup

class ParameterSetPlayerGroupForm(forms.ModelForm):
    '''
    parameterset player group edit form
    '''
    
    group_number = forms.IntegerField(label='Group Number (1-8)',
                                   min_value=1,
                                   max_value=8,
                                   widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_player_group.group_number",
                                                                   "step":"1",
                                                                   "min":"1"}))

    class Meta:
        model=ParameterSetPlayerGroup
        fields =['group_number',]
