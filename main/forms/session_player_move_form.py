'''
session player move form
'''

from django import forms

from django.utils.safestring import mark_safe

from main.models import SessionPlayerMove

class SessionPlayerMoveForm(forms.Form):
    '''
    session player move form
    '''
    good_one_amount = forms.IntegerField(label=mark_safe('<span v-bind:style = "{color : transfer_modal_good_one_rgb}">  [[transfer_modal_good_one_name]]</span> Amount'),
                                         min_value=0,
                                         max_value=9999,
                                         widget=forms.NumberInput(attrs={"step" : "1",
                                                                         "min" : "0",
                                                                         "value" : "0",
                                                                         "v-on:keyup.enter":"sendMoveGoods()"}))
    
    good_two_amount = forms.IntegerField(label=mark_safe('<span v-bind:style = "{color : transfer_modal_good_two_rgb}">  [[transfer_modal_good_two_name]]</span> Amount'),
                                         min_value=0,
                                         max_value=9999,
                                         widget=forms.NumberInput(attrs={"step" : "1",
                                                                         "min" : "0",
                                                                         "value" : "0",
                                                                         "v-on:keyup.enter":"sendMoveGoods()"}))
