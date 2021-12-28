'''
Parameterset edit form
'''

from django import forms

from main.models import ParameterSet

from main.globals import AvatarModes

class ParameterSetForm(forms.ModelForm):
    '''
    Parameterset edit form
    '''
    town_count = forms.IntegerField(label='Number of Towns (3 max)',
                                    min_value=1,
                                    max_value=3,
                                    widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.town_count",
                                                                    "step":"1",
                                                                    "max":"3",
                                                                    "min":"1"}))
    
    good_count = forms.IntegerField(label='Number of Goods (2 or 3)',
                                    min_value=2,
                                    max_value=3,
                                    widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.good_count",
                                                                    "step":"1",
                                                                    "max":"3",
                                                                    "min":"2"}))

    period_count = forms.IntegerField(label='Number of Periods',
                                      min_value=1,
                                      widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.period_count",
                                                                      "step":"1",
                                                                      "min":"1"}))

    period_length_production = forms.IntegerField(label='Production Length (seconds)',
                                                  min_value=1,
                                                  widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.period_length_production",
                                                                                  "step":"1",
                                                                                  "min":"1"}))
    
    period_length_trade = forms.IntegerField(label='Trade Length (seconds)',
                                             min_value=1,
                                             widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.period_length_trade",
                                                                             "step":"1",
                                                                             "min":"1"}))

    break_period_frequency = forms.IntegerField(label='Break Period Frequency (periods)',
                                                min_value=2,
                                                widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.break_period_frequency",
                                                                                "step":"1",
                                                                                "min":"1"}))

    allow_stealing = forms.ChoiceField(label='Allow Stealing',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.allow_stealing",}))
                                       
    private_chat = forms.ChoiceField(label='Private Chat',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.private_chat",}))
    
    show_avatars = forms.ChoiceField(label='Show Avatars',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.show_avatars",}))
    
    avatar_assignment_mode = forms.ChoiceField(label='Avatar Assignment',
                                       choices=AvatarModes.choices,
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.avatar_assignment_mode",}))
    
    avatar_grid_row_count = forms.IntegerField(label='Avatar Grid Row Count',
                                                min_value=1,
                                                widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.avatar_grid_row_count",
                                                                                "min":"1"}))
    
    avatar_grid_col_count = forms.IntegerField(label='Avatar Grid Column Count',
                                                min_value=1,
                                                widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.avatar_grid_col_count",
                                                                                "min":"1"}))
    avatar_grid_text = forms.CharField(label='Avatar Grid Text',
                            widget=forms.TextInput(attrs={"v-model":"session.parameter_set.avatar_grid_text",
                                                          })) 

    show_instructions = forms.ChoiceField(label='Show Instructions',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.show_instructions",}))

    test_mode = forms.ChoiceField(label='Test Mode',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.test_mode",}))

    class Meta:
        model=ParameterSet
        fields =['town_count','good_count', 'period_count', 'period_length_production' ,
                 'period_length_trade', 'break_period_frequency', 'allow_stealing' ,
                 'private_chat', 'show_avatars', 'avatar_assignment_mode', 'avatar_grid_row_count', 
                 'avatar_grid_col_count', 'avatar_grid_text', 'show_instructions', 'test_mode']
