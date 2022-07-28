'''
end game form
'''

from django import forms

class EndGameForm(forms.Form):
    '''
    end game form
    '''
    name =  forms.CharField(label='Enter your full name',
                            widget=forms.TextInput(attrs={"v-on:keyup.enter":"sendName()"}))

    student_id =  forms.CharField(label='Student ID',
                                  required=False,
                                  widget=forms.TextInput(attrs={"v-on:keyup.enter":"sendName()"}))
