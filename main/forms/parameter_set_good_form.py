'''
Parameterset good edit form
'''

from django import forms

from main.models import ParameterSetGood

class ParameterSetGoodForm(forms.ModelForm):
    '''
    Parameterset good edit form
    '''
    
    label = forms.CharField(label='Good Label',
                            widget=forms.TextInput(attrs={"v-model":"current_parameter_set_good.label",
                                                          "maxlength": "10"}))
    
    abbreviation = forms.CharField(label='Good Abbreviation',
                                    widget=forms.TextInput(attrs={"v-model":"current_parameter_set_good.abbreviation",
                                                                    "maxlength": "2"}))

    rgb_color = forms.CharField(label='Good RGB Color',
                                widget=forms.TextInput(attrs={"v-model":"current_parameter_set_good.rgb_color",
                                                              "maxlength": "10"}))

    class Meta:
        model=ParameterSetGood
        fields =['label', 'abbreviation', 'rgb_color', ]
