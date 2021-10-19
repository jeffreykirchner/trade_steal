'''
parameterset type player edit form
'''

from django import forms

from main.models import ParameterSetTypePlayer

class ParameterSetTypePlayerForm(forms.ModelForm):
    '''
    parameterset type player edit form
    '''
    title = forms.CharField(label='Title',
                            widget=forms.TextInput(attrs={"v-model":"session.title",
                                                           "v-on:keyup.enter":"sendUpdateSession()"}))

    class Meta:
        model=ParameterSetTypePlayer
        fields =['title']
