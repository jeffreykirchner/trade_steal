'''
session player move form
'''

from django import forms

from main.models import SessionPlayerMove

class SessionPlayerMoveForm(forms.Form):
    '''
    session player move form
    '''
    good_one_amount = forms.IntegerField(label='Good One Amount',
                                         min_value=0,
                                         max_value=9999,
                                         widget=forms.NumberInput(attrs={"step" : "1",
                                                                         "min" : "0"}))
    
    good_two_amount = forms.IntegerField(label='Good Two Amount',
                                         min_value=0,
                                         max_value=9999,
                                         widget=forms.NumberInput(attrs={"step" : "1",
                                                                         "min" : "0"}))
