'''
instruction form admin screen
'''
from django import forms
from main.models import Instruction
from tinymce.widgets import TinyMCE

class InstructionFormAdmin(forms.ModelForm):
    '''
    instruction form admin screen
    '''

    page_number = forms.IntegerField(label='Page Number',
                                     min_value=1,
                                     widget=forms.NumberInput(attrs={"min":"1"}))
    
    label = forms.CharField(label='Page Label',
                            widget=forms.TextInput(attrs={"size":"50"}))

    text_html = forms.CharField(label='Page HTML Text',
                                widget=TinyMCE(attrs={"rows":20, "cols":200}))

    class Meta:
        model=Instruction
        fields = ('page_number', 'label', 'text_html')