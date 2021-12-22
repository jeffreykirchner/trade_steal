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
     
    avatar = forms.ModelChoiceField(label='Avatar',
                                    required=False,
                                    queryset=Avatar.objects.all(),
                                    widget=forms.Select(attrs={"v-model":"current_parameter_set_avatar.avatar.id"}))

    class Meta:
        model=ParameterSetAvatar
        fields =['avatar']
    
