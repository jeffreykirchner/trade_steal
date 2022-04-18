'''
instruction form admin screen
'''
from django import forms
from main.models import InstructionSet
from tinymce.widgets import TinyMCE

class InstructionSetFormAdmin(forms.ModelForm):
    '''
    instruction set form admin screen
    '''

    label = forms.CharField(label='Instruction Set Name',
                            widget=forms.TextInput(attrs={"width":"100px"}))
    
    action_page_production = forms.IntegerField(label='Production Action Page',
                                                min_value=1,
                                                widget=forms.NumberInput(attrs={"width":"100px"}))
    
    action_page_move = forms.IntegerField(label='Move Action Page',
                                                min_value=1,
                                                widget=forms.NumberInput(attrs={"width":"100px"}))

    action_page_chat = forms.IntegerField(label='Chat Action Page',
                                                min_value=1,
                                                widget=forms.NumberInput(attrs={"width":"100px"}))

    class Meta:
        model=InstructionSet
        fields = ('label','action_page_production', 'action_page_move', 'action_page_chat')
    

    def clean_action_page_move(self):
       
        action_page_production = self.cleaned_data.get("action_page_production")
        action_page_move = self.cleaned_data.get("action_page_move")
       

        if action_page_move <= action_page_production:
            self.add_error('action_page_move', "Must be after the Production page.")           
        
        return action_page_move
    
    def clean_action_page_chat(self):
       
        action_page_chat = self.cleaned_data.get("action_page_chat")
        action_page_move = self.cleaned_data.get("action_page_move")
       

        if action_page_chat <= action_page_move:
            self.add_error('action_page_chat', "Must be after the Move page.")           
        
        return action_page_chat