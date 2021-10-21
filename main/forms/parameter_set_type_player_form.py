'''
parameterset type player edit form
'''

from django import forms

from main.models import ParameterSetPlayer

class ParameterSetTypePlayerForm(forms.ModelForm):
    '''
    parameterset type player edit form
    '''
    id_label = forms.CharField(label='Player Label',
                               widget=forms.TextInput(attrs={"v-model":"current_parameter_set_type_player.id_label",}))
    
    location = forms.CharField(label='Screen Location (1-8)',
                               widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_type_player.location",
                                                               "step":"1",
                                                                "min":"1"}))

    class Meta:
        model=ParameterSetPlayer
        fields =['id_label', 'location']
