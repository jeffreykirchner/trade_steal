'''
parameterset avatar edit form
'''

from django import forms

from main.models import Avatar
from main.models.parameter_set_avatar import ParameterSetAvatar

class ParameterSetAvatarForm(forms.ModelForm):
    '''
    parameterset avatar edit form
    '''    
    grid_location_row = forms.IntegerField(label='Grid Location Row',
                                  min_value=1,
                                  widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_avatar.grid_location_row",
                                                                  "min":"1",
                                                                  }))

    grid_location_col = forms.IntegerField(label='Grid Location Column',
                                  min_value=1,
                                  widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_avatar.grid_location_col",
                                                                  "min":"1",
                                                                  }))
    
    avatar = forms.ModelChoiceField(label='Avatar',
                                    empty_label=None,
                                    queryset=Avatar.objects.all(),
                                    widget=forms.Select(attrs={"v-model":"current_parameter_set_avatar.avatar.id"}))

    class Meta:
        model=ParameterSetAvatar
        fields =['grid_location_row', 'grid_location_col', 'avatar']
    
