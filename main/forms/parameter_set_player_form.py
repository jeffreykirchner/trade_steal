'''
parameterset type player edit form
'''

from django import forms

from main.models import ParameterSetPlayer
from main.globals import SubjectType

class ParameterSetPlayerForm(forms.ModelForm):
    '''
    parameterset player edit form
    '''
    id_label = forms.CharField(label='Player Label',
                               widget=forms.TextInput(attrs={"v-model":"current_parameter_set_player.id_label",}))
    
    location = forms.CharField(label='Screen Location (1-8)',
                               widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_player.location",
                                                               "step":"1",
                                                               "min":"1"}))
    
    subject_type = forms.ChoiceField(label='Subject Type',
                                     choices=SubjectType.choices,
                                     widget=forms.Select(attrs={"v-model":"current_parameter_set_player.subject_type"}))

    class Meta:
        model=ParameterSetPlayer
        fields =['id_label', 'location', 'subject_type']
