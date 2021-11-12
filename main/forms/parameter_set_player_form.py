'''
parameterset player edit form
'''

from django import forms
from django.db.models.query import RawQuerySet

from main.models import ParameterSetPlayer
from main.models import ParameterSetGood
from main.globals import SubjectType

class ParameterSetPlayerForm(forms.ModelForm):
    '''
    parameterset player edit form
    '''

    id_label = forms.CharField(label='Player Label',
                               widget=forms.TextInput(attrs={"v-model":"current_parameter_set_player.id_label",}))
    
    location = forms.CharField(label='Screen Location (1-8)',
                               widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_player.location",
                                                               "step":"1",
                                                               "min":"1"}))
    
    subject_type = forms.ChoiceField(label='Subject Type',
                                     choices=SubjectType.choices,
                                     widget=forms.Select(attrs={"v-model":"current_parameter_set_player.subject_type"}))

    good_one = forms.ModelChoiceField(label='First Good',
                                      empty_label=None,
                                      queryset=ParameterSetGood.objects.none(),
                                      widget=forms.Select(attrs={"v-model":"current_parameter_set_player.good_one.id"}))
    
    good_two = forms.ModelChoiceField(label='Second Good',
                                      empty_label=None,
                                      queryset=ParameterSetGood.objects.none(),
                                      widget=forms.Select(attrs={"v-model":"current_parameter_set_player.good_two.id"}))

    good_three = forms.ModelChoiceField(label='Third Good',
                                        empty_label=None,
                                        queryset=ParameterSetGood.objects.none(),
                                        widget=forms.Select(attrs={"v-model":"current_parameter_set_player.good_three.id"}))

    class Meta:
        model=ParameterSetPlayer
        fields =['id_label', 'location', 'subject_type', 'good_one', 'good_two', 'good_three']
    
    def clean(self):
        cleaned_data = super().clean()
        good_one = cleaned_data.get("good_one")
        good_two = cleaned_data.get("good_two")
        good_three = cleaned_data.get("good_three")

        if good_one == good_two:
            self.add_error('good_one', "Must be unique.")
            self.add_error('good_two', "Must be unique.")
        
        if good_one == good_three:
            self.add_error('good_one', "Must be unique.")
            self.add_error('good_three', "Must be unique.")
        
        if good_two == good_three:
            self.add_error('good_two', "Must be unique.")
            self.add_error('good_three', "Must be unique.")
