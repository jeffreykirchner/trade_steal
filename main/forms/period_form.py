'''
value cost edit form
'''

from django import forms

from main.models import ParameterSetPeriod

class PeriodForm(forms.ModelForm):
    '''
    value cost edit form
    '''
    price_cap = forms.DecimalField(label='Price Cap',
                                    min_value=0,
                                    widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.periods[current_visible_period-1].price_cap",
                                                                    "v-on:keyup.enter":"sendUpdatePeriod()",
                                                                    "step":"0.25"}))
    
    price_cap_enabled = forms.ChoiceField(label='Enabled',
                                          choices=((True, 'Yes'), (False,'No' )),
                                          widget=forms.Select(attrs={"v-model":"session.parameter_set.periods[current_visible_period-1].price_cap_enabled",
                                                                     "v-on:keyup.enter":"sendUpdatePeriod()",}))

    y_scale_max = forms.DecimalField(label='Y Scale Max (Price)',
                                     min_value=1,
                                     widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.periods[current_visible_period-1].y_scale_max",
                                                                     "v-on:keyup.enter":"sendUpdatePeriod()",
                                                                     "step":"1"}))

    x_scale_max = forms.DecimalField(label='X Scale Max (Units Traded)',
                                     min_value=1,
                                     widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.periods[current_visible_period-1].x_scale_max",
                                                                     "v-on:keyup.enter":"sendUpdatePeriod()",
                                                                     "step":"1"}))

    class Meta:
        model=ParameterSetPeriod
        fields =['price_cap', 'price_cap_enabled', 'y_scale_max', 'x_scale_max']
