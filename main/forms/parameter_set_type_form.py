'''
parameter set type edit form
'''

from django import forms

from main.models import ParameterSetType

class ParameterSetTypeForm(forms.ModelForm):
    '''
    parameter set type edit form
    '''
    good_one_amount = forms.CharField(label='Good One Required Earn ¢ (Max of G1 and G2)',
                                      widget=forms.NumberInput(attrs={"v-model":"current_parameterset_type.good_one_amount",
                                                                      "step":"1",
                                                                      "min":"1"}))
    
    good_two_amount = forms.CharField(label='Good Two Required Earn ¢ (Max of G1 and G2)',
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

    ce_earnings = forms.IntegerField(label='Earnings at Completive Equilibrium (¢)',
                                     min_value=0,
                                     widget=forms.NumberInput(attrs={"v-model":"current_parameterset_type.ce_earnings",
                                                                     "step":"1"}))  

    autarky_earnings = forms.IntegerField(label='Earnings at Autarky (¢)',
                                     min_value=0,
                                     widget=forms.NumberInput(attrs={"v-model":"current_parameterset_type.autarky_earnings",
                                                                     "step":"1"}))                                                                                                                                        

    class Meta:
        model=ParameterSetType
        fields =['good_one_production_1','good_one_production_2', 'good_one_production_3',
                 'good_two_production_1','good_two_production_2', 'good_two_production_3',
                 'good_one_amount', 'good_two_amount',
                 'ce_earnings', 'autarky_earnings']
