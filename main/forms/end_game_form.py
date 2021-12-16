'''
end game form
'''

from django import forms

from django.utils.safestring import mark_safe

from main.models import SessionPlayerMove

class EndGameForm(forms.Form):
    '''
    end game form
    '''
    name =  forms.CharField(label='Enter your full name',
                            )
    
    student_id =  forms.CharField(label='Student ID', required=False)
