'''
parameter set type edit form
'''

from django import forms

from main.models import ParameterSetType

class ParameterSetTypeForm(forms.ModelForm):
    '''
    parameter set type edit form
    '''
    title = forms.CharField(label='Title',
                            widget=forms.TextInput(attrs={"v-model":"session.title",
                                                           "v-on:keyup.enter":"sendUpdateSession()"}))

    class Meta:
        model=ParameterSetType
        fields =['title']
