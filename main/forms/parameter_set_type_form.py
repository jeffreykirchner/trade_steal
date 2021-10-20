'''
parameter set type edit form
'''

from django import forms

from main.models import ParameterSetType

class ParameterSetTypeForm(forms.ModelForm):
    '''
    parameter set type edit form
    '''
    good_one_amount = forms.CharField(label='Good One Amount to Earn 1¢',
                                      widget=forms.NumberInput(attrs={"v-model":"current_parameterset_type.good_one_amount",
                                                                      "step":"1",
                                                                      "min":"1"}))
    
    good_two_amount = forms.CharField(label='Good Two Amount to Earn 1¢',
                                      widget=forms.NumberInput(attrs={"v-model":"current_parameterset_type.good_two_amount",
                                                                      "step":"1",
                                                                      "min":"1"}))
                    
    good_one_production_1 = forms.DecimalField(label='Good One P1',
                                    min_value=0,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameterset_type.good_one_production_1",
                                                                    "step":"0.01"}))
    good_one_production_2 = forms.DecimalField(label='Good One P2',
                                    min_value=0,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameterset_type.good_one_production_2",
                                                                    "step":"0.01"}))  

    good_one_production_3 = forms.DecimalField(label='Good One P3',
                                    min_value=0,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameterset_type.good_one_production_3",
                                                                    "step":"0.01"})) 

    good_two_production_1 = forms.DecimalField(label='Good Two P1',
                                    min_value=0,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameterset_type.good_two_production_1",
                                                                    "step":"0.01"}))
    good_two_production_2 = forms.DecimalField(label='Good Two P2',
                                    min_value=0,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameterset_type.good_two_production_2",
                                                                    "step":"0.01"}))  

    good_two_production_3 = forms.DecimalField(label='Good Two P3',
                                    min_value=0,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameterset_type.good_two_production_3",
                                                                    "step":"0.01"}))                                                                                                                                             

    class Meta:
        model=ParameterSetType
        fields =['good_one_amount', 'good_two_amount',
                 'good_one_production_1','good_one_production_2', 'good_one_production_3',
                 'good_two_production_1','good_two_production_2', 'good_two_production_3']
